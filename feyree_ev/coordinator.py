"""Coordinator para la integración Feyree EV."""

import logging
import socket
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class FeyreeEVCoordinator(DataUpdateCoordinator):
    """Coordinator para obtener datos del cargador Feyree EV."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        """Inicializar el coordinator."""
        self.entry = entry
        self.device_id = entry.data.get("device_id")
        self.device_ip = entry.data.get("device_ip")
        self.local_key = entry.data.get("local_key")
        self.version = entry.data.get("version", 3.5)
        self._discovering = False

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.device_id}",
            update_interval=timedelta(seconds=30),
        )

    def _find_device_ip(self) -> str | None:
        """Escanear la red para encontrar la IP del dispositivo."""
        import tinytuya

        _LOGGER.info("Escaneando red para encontrar dispositivo %s...", self.device_id)
        try:
            devices = tinytuya.deviceScan()
            for dev_id, dev in devices.items():
                gw_id = dev.get("gwId", "")
                if self.device_id.lower() in gw_id.lower():
                    ip = dev.get("ip")
                    if ip:
                        _LOGGER.info("Dispositivo encontrado en %s", ip)
                        return ip
        except Exception as err:
            _LOGGER.error("Error escaneando red: %s", err)
        return None

    def _update_config_ip(self, new_ip: str) -> None:
        """Actualizar la IP en la config entry."""
        if self.entry and hasattr(self.entry, "data"):
            new_data = dict(self.entry.data)
            new_data["device_ip"] = new_ip
            try:
                self.hass.config_entries.async_update_entry(self.entry, data=new_data)
                _LOGGER.info("IP actualizada en config: %s", new_ip)
            except Exception as err:
                _LOGGER.error("Error actualizando IP en config: %s", err)

    def _get_status_with_ip(self, ip: str) -> dict | None:
        """Intentar obtener status con una IP específica."""
        import tinytuya

        d = tinytuya.Device(
            self.device_id,
            ip,
            self.local_key,
            version=self.version,
        )
        d.set_version(self.version)
        d.set_socketTimeout(3)
        d.set_socketPersistent(False)
        return d.status()

    async def _async_update_data(self):
        """Obtener datos del dispositivo en un executor."""
        try:
            import tinytuya

            def _try_connect():
                # Intento 1: IP configurada
                if self.device_ip:
                    _LOGGER.debug("Intentando conexión con %s", self.device_ip)
                    try:
                        status = self._get_status_with_ip(self.device_ip)
                        if status and "dps" in status:
                            return status["dps"], None
                    except Exception:
                        pass

                # Intento 2: Escanear red
                _LOGGER.info("Conexión fallida, escaneando red...")
                new_ip = self._find_device_ip()
                if new_ip:
                    try:
                        status = self._get_status_with_ip(new_ip)
                        if status and "dps" in status:
                            self.device_ip = new_ip
                            return status["dps"], new_ip
                    except Exception:
                        pass

                return None, None

            status, new_ip = await self.hass.async_add_executor_job(_try_connect)

            if not status:
                raise UpdateFailed("No se pudieron obtener datos del dispositivo")

            if new_ip:
                self._update_config_ip(new_ip)

            return status

        except Exception as err:
            raise UpdateFailed(f"Error comunicando con el dispositivo: {err}") from err

    async def async_set_value(self, dps_id: str, value) -> bool:
        """Establecer un valor en el dispositivo (ejecutado en executor)."""
        try:
            import tinytuya

            def _set_value():
                d = tinytuya.Device(
                    self.device_id,
                    self.device_ip,
                    self.local_key,
                    version=self.version,
                )
                d.set_version(self.version)
                d.set_socketPersistent(True)
                return d.set_value(int(dps_id), value)

            await self.hass.async_add_executor_job(_set_value)
            await self.async_request_refresh()
            return True

        except Exception as err:
            _LOGGER.error(f"Error estableciendo DPS {dps_id}: {err}")
            return False

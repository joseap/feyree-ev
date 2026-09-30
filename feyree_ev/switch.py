"""Switch platform para la integración Feyree EV (monofásico)."""

import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FeyreeEVCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Configuración de la plataforma switch."""
    coordinator: FeyreeEVCoordinator = hass.data[DOMAIN][entry.entry_id]
    switch = ChargeEnableSwitch(coordinator)
    async_add_entities([switch])


class ChargeEnableSwitch(CoordinatorEntity[FeyreeEVCoordinator], SwitchEntity):
    """Switch para Charge Enable (DPS 124)."""

    def __init__(self, coordinator: FeyreeEVCoordinator):
        """Inicializar el switch."""
        super().__init__(coordinator)
        self._dps_id = "124"
        self._attr_name = "Charge Enable"
        self._attr_unique_id = f"feyree_{coordinator.device_id}_{self._dps_id}"

    @property
    def is_on(self):
        """Retornar el estado actual."""
        return bool(self.coordinator.data.get(self._dps_id, False))

    async def async_turn_on(self, **kwargs) -> None:
        """Activar carga."""
        await self.coordinator.async_set_value(self._dps_id, True)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Desactivar carga."""
        await self.coordinator.async_set_value(self._dps_id, False)
        self.async_write_ha_state()

    @property
    def available(self):
        """Retornar si el dispositivo está disponible."""
        return self.coordinator.last_update_success

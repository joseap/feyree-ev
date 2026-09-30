"""Number platform para la integración Feyree EV (monofásico)."""

import logging
from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FeyreeEVCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Configuración de la plataforma number."""
    coordinator: FeyreeEVCoordinator = hass.data[DOMAIN][entry.entry_id]

    dps_numbers = [
        {"id": "115", "name": "Corriente preset", "unit": "A", "min": 6, "max": 32, "step": 1},
        {"id": "125", "name": "Corriente máxima", "unit": "A", "min": 6, "max": 32, "step": 1},
    ]

    numbers = []
    for dps_config in dps_numbers:
        numbers.append(TinyTuyaNumber(coordinator, dps_config))

    async_add_entities(numbers)


class TinyTuyaNumber(CoordinatorEntity[FeyreeEVCoordinator], NumberEntity):
    """Number para DPS ajustables de dispositivo Tuya."""

    def __init__(self, coordinator: FeyreeEVCoordinator, dps_config: dict):
        """Inicializar el number."""
        super().__init__(coordinator)
        self._dps_id = dps_config["id"]
        self._attr_name = f"{dps_config['name']}"
        self._attr_unique_id = f"feyree_{coordinator.device_id}_{dps_config['id']}"
        self._attr_native_min_value = dps_config["min"]
        self._attr_native_max_value = dps_config["max"]
        self._attr_native_step = dps_config["step"]
        self._attr_native_unit_of_measurement = dps_config.get("unit")
        self._attr_mode = NumberMode.BOX

    @property
    def native_value(self):
        """Retornar el valor actual."""
        return self.coordinator.data.get(self._dps_id)

    async def async_set_native_value(self, value: float) -> None:
        """Establecer un nuevo valor."""
        await self.coordinator.async_set_value(self._dps_id, int(value))
        self.async_write_ha_state()

    @property
    def available(self):
        """Retornar si el dispositivo está disponible."""
        return self.coordinator.last_update_success

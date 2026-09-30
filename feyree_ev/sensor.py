"""Sensor platform para la integración Feyree EV (monofásico)."""

import logging
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfPower,
    UnitOfEnergy,
    UnitOfTemperature,
    PERCENTAGE,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FeyreeEVCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Configuración de la plataforma sensor."""
    coordinator: FeyreeEVCoordinator = hass.data[DOMAIN][entry.entry_id]

    dps_sensors = [
        {"id": "102", "name": "Voltaje", "unit": "V", "device_class": SensorDeviceClass.VOLTAGE, "scale": 0.1},
        {"id": "105", "name": "Corriente", "unit": "A", "device_class": SensorDeviceClass.CURRENT, "scale": 0.1},
        {"id": "109", "name": "Potencia", "unit": "kW", "device_class": SensorDeviceClass.POWER, "scale": 0.1},
        {"id": "110", "name": "Temperatura", "unit": "°C", "device_class": SensorDeviceClass.TEMPERATURE, "scale": 0.1},
        {"id": "112", "name": "Energía sesión", "unit": "kWh", "device_class": SensorDeviceClass.ENERGY, "scale": 0.1},
    ]

    dps_text_sensors = [
        {"id": "101", "name": "Estado carga", "device_class": None},
        {"id": "10", "name": "Fault Code", "device_class": None},
    ]

    sensors = []
    for dps_config in dps_sensors:
        sensors.append(TinyTuyaSensor(coordinator, dps_config))
    for dps_config in dps_text_sensors:
        sensors.append(TinyTuyaTextSensor(coordinator, dps_config))

    async_add_entities(sensors)


class TinyTuyaSensor(CoordinatorEntity[FeyreeEVCoordinator], SensorEntity):
    """Sensor para DPS de dispositivo Tuya."""

    def __init__(self, coordinator: FeyreeEVCoordinator, dps_config: dict):
        """Inicializar el sensor."""
        super().__init__(coordinator)
        self._dps_id = dps_config["id"]
        self._attr_name = f"{dps_config['name']}"
        self._attr_unique_id = f"feyree_{coordinator.device_id}_{dps_config['id']}"
        self._attr_native_unit_of_measurement = dps_config.get("unit")
        self._attr_device_class = dps_config.get("device_class")
        self._attr_state_class = (
            SensorStateClass.TOTAL_INCREASING
            if dps_config.get("device_class") == SensorDeviceClass.ENERGY
            else SensorStateClass.MEASUREMENT
            if dps_config.get("device_class")
            else None
        )
        self._scale = dps_config.get("scale", 1)

    @property
    def native_value(self):
        """Retornar el valor actual."""
        val = self.coordinator.data.get(self._dps_id)
        if isinstance(val, (int, float)) and self._scale != 1:
            return round(val * self._scale, 1)
        return val

    @property
    def available(self):
        """Retornar si el dispositivo está disponible."""
        return self.coordinator.last_update_success


class TinyTuyaTextSensor(CoordinatorEntity[FeyreeEVCoordinator], SensorEntity):
    """Sensor de texto para DPS de dispositivo Tuya."""

    def __init__(self, coordinator: FeyreeEVCoordinator, dps_config: dict):
        """Inicializar el sensor de texto."""
        super().__init__(coordinator)
        self._dps_id = dps_config["id"]
        self._attr_name = f"{dps_config['name']}"
        self._attr_unique_id = f"feyree_{coordinator.device_id}_{dps_config['id']}"
        self._attr_device_class = dps_config.get("device_class")

    @property
    def native_value(self):
        """Retornar el valor actual."""
        return self.coordinator.data.get(self._dps_id)

    @property
    def available(self):
        """Retornar si el dispositivo está disponible."""
        return self.coordinator.last_update_success

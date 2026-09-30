"""Integración Feyree EV para Home Assistant.

Permite la comunicación local directa con cargadores de vehículos eléctricos Tuya.
"""

import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .coordinator import FeyreeEVCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Configuración básica de la integración."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configuración de la entrada de configuración."""
    coordinator = FeyreeEVCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(
        entry, ["switch", "sensor", "number"]
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Desinstalación de la entrada de configuración."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, ["switch", "sensor", "number"]
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
"""
Flujo de configuración para la integración Feyree EV.
"""

import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_DEVICE_ID, CONF_DEVICE_IP, CONF_LOCAL_KEY, CONF_VERSION, DEFAULT_VERSION

_LOGGER = logging.getLogger(__name__)


class FeyreeEVConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Flujo de configuración para Feyree EV."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Paso inicial del flujo de configuración."""
        errors = {}
        
        if user_input is not None:
            # Validar entradas
            if not user_input.get(CONF_DEVICE_ID):
                errors[CONF_DEVICE_ID] = "required"
            elif not user_input.get(CONF_DEVICE_IP):
                errors[CONF_DEVICE_IP] = "required"
            elif not user_input.get(CONF_LOCAL_KEY):
                errors[CONF_LOCAL_KEY] = "required"
            else:
                return self.async_create_entry(
                    title="Feyree EV",
                    data=user_input
                )

        # Pre-cargar con tus datos específicos
        data_schema = vol.Schema({
            vol.Required(CONF_DEVICE_ID, default="bfd76e91"): str,
            vol.Required(CONF_DEVICE_IP, default="192.168.1.36"): str,
            vol.Required(CONF_LOCAL_KEY, default="<F@9!:xTq4*@WedS"): str,
            vol.Optional(CONF_VERSION, default=3.5): float,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Obtener el flujo de opciones."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Manejador del flujo de opciones."""

    def __init__(self, config_entry):
        """Inicializar el manejador de opciones."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Paso inicial del flujo de opciones."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema({
            vol.Required(
                "scan_interval",
                default=self.config_entry.options.get("scan_interval", 30),
            ): int,
        })

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema
        )
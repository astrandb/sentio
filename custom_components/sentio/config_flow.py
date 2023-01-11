"""Config flow for sentio sauna integration."""
import logging

import voluptuous as vol
from homeassistant import config_entries, exceptions
from homeassistant.core import HomeAssistant
from pysentio import SentioPro

from .const import (  # pylint:disable=unused-import
    BAUD_RATE,
    DEFAULT_SERIAL_PORT,
    DOMAIN,
    FAN_DISABLED,
    SERIAL_PORT,
)

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(SERIAL_PORT, default=DEFAULT_SERIAL_PORT): str,
        vol.Required(FAN_DISABLED, default=False): bool,
    }
)


class SentioHub:
    """
    TODO Remove this placeholder class and replace with things from your PyPI package.
    """

    type = None

    def __init__(self, host):
        """Initialize."""
        self.host = host

    async def connect(self, serial_port) -> bool:
        """Test if we can authenticate with the host."""
        api = SentioPro(serial_port, BAUD_RATE)
        api.get_config()
        self.type = api.type
        return True


async def validate_input(hass: HomeAssistant, data):
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """

    hub = SentioHub(data[SERIAL_PORT])

    if not await hub.connect(data[SERIAL_PORT]):
        raise CannotConnect

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": f"Sentio Pro {hub.type}"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for sentio sauna."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                await self.async_set_unique_id("sentio_xxx")
                self._abort_if_unique_id_configured()

                info = await validate_input(self.hass, user_input)

                return self.async_create_entry(title=info["title"], data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""

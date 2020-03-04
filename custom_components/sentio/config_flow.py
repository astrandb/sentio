"""Config flow for sentio sauna integration."""
import logging

import voluptuous as vol

from homeassistant import config_entries, core, exceptions
from pysentio import SentioPro

from .const import BAUD_RATE, DEFAULT_SERIAL_PORT, DOMAIN, SERIAL_PORT  # pylint:disable=unused-import

_LOGGER = logging.getLogger(__name__)

# TODO adjust the data schema to the data that you need
DATA_SCHEMA = vol.Schema({vol.Required(SERIAL_PORT, default=DEFAULT_SERIAL_PORT): str})


class SentioHub:
    """
    TODO Remove this placeholder class and replace with things from your PyPI package.
    """

    def __init__(self, host):
        """Initialize."""
        self.host = host

    async def connect(self, serial_port) -> bool:
        """Test if we can authenticate with the host."""
        ss = SentioPro(serial_port, BAUD_RATE)
        ss.get_config()
        self._type = ss.type
        return True

async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data["username"], data["password"]
    # )

    hub = SentioHub(data[SERIAL_PORT])

    if not await hub.connect(data[SERIAL_PORT]):
        raise CannotConnect

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": "Sentio Pro {}".format(hub._type)}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for sentio sauna."""

    VERSION = 1
    # TODO pick one of the available connection classes in homeassistant/config_entries.py
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                await self.async_set_unique_id('sentio_xxx')
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

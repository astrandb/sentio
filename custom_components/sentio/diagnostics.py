"""Diagnostics support for Sentio."""

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant

from . import SentioConfigEntry

TO_REDACT = {
    CONF_PASSWORD,
    CONF_USERNAME,
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: SentioConfigEntry
) -> dict:
    """Return diagnostics for a config entry."""

    _api = config_entry.runtime_data.client

    config_dict = {}
    for line in _api.config_raw.lower().splitlines():
        res = line.rsplit(" ", 1)
        val = res[1] if len(res) == 2 else None
        if res[0] != "config":
            config_dict[res[0]] = val

    config_data = {
        "type": _api.type,
        "sw_version": _api.sw_version,
        "config": config_dict,
    }

    return {
        "setup": async_redact_data(config_entry.data, TO_REDACT),
        "info": async_redact_data(config_data, TO_REDACT),
    }

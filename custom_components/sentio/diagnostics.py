"""Diagnostics support for Sentio."""
from __future__ import annotations

from pysentio import SentioPro

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant

from .const import DOMAIN

TO_REDACT = {
    CONF_PASSWORD,
    CONF_USERNAME,
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> dict:
    """Return diagnostics for a config entry."""

    _api: SentioPro = hass.data[DOMAIN][config_entry.entry_id]

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

    diagnostics_data = {
        "setup": async_redact_data(config_entry.data, TO_REDACT),
        "info": async_redact_data(config_data, TO_REDACT),
    }

    return diagnostics_data

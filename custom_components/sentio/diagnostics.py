"""Diagnostics support for Sentio."""
from __future__ import annotations

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from pysentio import SentioPro

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
    config_data = {
        "type": _api.type,
        "sw_version": _api.sw_version,
        "config": _api.config_raw,
    }

    diagnostics_data = {
        "setup": async_redact_data(config_entry.data, TO_REDACT),
        "info": async_redact_data(config_data, TO_REDACT),
    }

    return diagnostics_data

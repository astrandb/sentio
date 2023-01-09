"""The sentio sauna integration."""
import asyncio
import logging
from datetime import timedelta

# import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.event import async_track_time_interval
from pysentio import SentioPro

from .const import BAUD_RATE, DOMAIN, SERIAL_PORT, SIGNAL_UPDATE_SENTIO

# CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

PLATFORMS = ["light", "sensor", "switch", "fan", "climate"]

SCAN_INTERVAL = timedelta(seconds=60)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the sentio sauna component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up sentio sauna from a config entry."""

    def poll_update(event_time):
        _LOGGER.debug("Entered pollupdate")
        _api.update()
        _LOGGER.debug("Calling dispatcher_send")
        dispatcher_send(hass, SIGNAL_UPDATE_SENTIO)

    # TODO Store an API object for your platforms to access
    hass.data[DOMAIN] = {}
    hass.data[DOMAIN][entry.entry_id] = SentioPro(
        entry.data.get(SERIAL_PORT), BAUD_RATE
    )  # MyApi(...)
    _api = hass.data[DOMAIN][entry.entry_id]
    _api.get_config()
    _LOGGER.info("SW_version: %s, Type: %s", _api.sw_version, _api.type)
    device_info = DeviceInfo(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, "4321")},
        manufacturer="Sentiotec",
        model=f"Pro {_api.type}",
        name="Sauna",
        sw_version=_api.sw_version,
    )
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(**device_info)

    """Get initial states and data from API"""
    _api.update()

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    async_track_time_interval(hass, poll_update, SCAN_INTERVAL)
    dispatcher_send(hass, SIGNAL_UPDATE_SENTIO)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

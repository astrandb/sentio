"""The sentio sauna integration."""
import asyncio
import logging
from datetime import timedelta

# import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.event import async_track_time_interval
from pysentio import SentioPro

from .const import BAUD_RATE, DOMAIN, MANUFACTURER, SERIAL_PORT, SIGNAL_UPDATE_SENTIO

# CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

PLATFORMS = [
    Platform.LIGHT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.FAN,
    Platform.CLIMATE,
    Platform.HUMIDIFIER,
]

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

    hass.data[DOMAIN] = {}
    hass.data[DOMAIN][entry.entry_id] = SentioPro(
        entry.data.get(SERIAL_PORT), BAUD_RATE
    )
    _api = hass.data[DOMAIN][entry.entry_id]
    _api.get_config()
    _LOGGER.info("SW_version: %s, Type: %s", _api.sw_version, _api.type)
    device_info = DeviceInfo(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, "4321")},
        manufacturer=MANUFACTURER,
        model=f"Pro {_api.type}",
        name="Sauna",
        sw_version=_api.sw_version,
    )
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(**device_info)

    # Get initial states and data from API
    _api.update()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async_track_time_interval(hass, poll_update, SCAN_INTERVAL)
    dispatcher_send(hass, SIGNAL_UPDATE_SENTIO)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Migrate old entry."""
    _LOGGER.info("Migrating from version %s", config_entry.version)

    if config_entry.version == 1:

        data = {**config_entry.data}
        if "disable_fan" in data:
            data.pop("disable_fan")
        config_entry.data = {**data}
        config_entry.version = 2

    _LOGGER.info("Migration to version %s successful", config_entry.version)
    return True

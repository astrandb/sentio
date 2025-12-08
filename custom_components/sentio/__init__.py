"""The sentio sauna integration."""

from dataclasses import dataclass
from datetime import timedelta
import logging

from pysentio import SentioPro

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    BAUD_RATE,
    DOMAIN,
    HEATER_POWER,
    MANUFACTURER,
    SERIAL_PORT,
    SIGNAL_UPDATE_SENTIO,
    UNIQUE_IDENTIFIER,
)

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

type SentioConfigEntry = ConfigEntry[SentioData]


@dataclass
class SentioData:
    """Class for config entry data."""

    client: SentioPro


async def async_setup_entry(hass: HomeAssistant, entry: SentioConfigEntry):
    """Set up sentio sauna from a config entry."""

    def poll_update(event_time):
        _LOGGER.debug("Entered pollupdate")
        _api.update()
        _LOGGER.debug("Calling dispatcher_send")
        dispatcher_send(hass, SIGNAL_UPDATE_SENTIO)

    client = SentioPro(entry.data.get(SERIAL_PORT), BAUD_RATE)
    entry.runtime_data = SentioData(client)

    _api = entry.runtime_data.client
    _api.get_config()
    _LOGGER.info("SW_version: %s, Type: %s", _api.sw_version, _api.type)
    device_info = DeviceInfo(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, UNIQUE_IDENTIFIER)},
        manufacturer=MANUFACTURER,
        model=f"Pro {_api.type}",
        translation_key="sauna",
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


async def async_unload_entry(hass: HomeAssistant, entry: SentioConfigEntry):
    """Unload the config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_migrate_entry(hass: HomeAssistant, config_entry: SentioConfigEntry):
    """Migrate old entry."""
    _LOGGER.info("Migrating from version %s", config_entry.version)

    if config_entry.version == 1:
        data = {**config_entry.data}
        if "disable_fan" in data:
            data.pop("disable_fan")
        hass.config_entries.async_update_entry(config_entry, data={**data})
        hass.config_entries.async_update_entry(config_entry, version=2)

    if config_entry.version == 2:
        data = {**config_entry.data}
        if HEATER_POWER not in data:
            data[HEATER_POWER] = 0
        hass.config_entries.async_update_entry(config_entry, data={**data})
        hass.config_entries.async_update_entry(config_entry, version=3)

    _LOGGER.info("Migration to version %s successful", config_entry.version)
    return True

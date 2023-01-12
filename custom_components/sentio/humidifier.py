"""Humidifier component for Sentio sauna controller"""

import logging

from homeassistant.components.humidifier import (
    HumidifierDeviceClass,
    HumidifierEntity,
    HumidifierEntityDescription,
    HumidifierEntityFeature,
)
from homeassistant.components.humidifier.const import MODE_NORMAL

from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect, dispatcher_send
from homeassistant.helpers.entity import DeviceInfo
from pysentio import PYS_STATE_OFF, PYS_STATE_ON

from .const import DOMAIN, HUMIDITY_MODELS, SIGNAL_UPDATE_SENTIO

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup the humidifier entities."""

    def get_humidifiers():
        api = hass.data[DOMAIN][entry.entry_id]
        entities = []
        if api.type.upper() in HUMIDITY_MODELS:
            entities.append(SaunaHumidifier(hass, entry, vaporizer_desc))
        return entities

    async_add_entities(await hass.async_add_job(get_humidifiers), True)


vaporizer_desc = HumidifierEntityDescription(
    key="vaporizer",
    device_class=HumidifierDeviceClass.HUMIDIFIER,
    name="Vaporizer",
)


class SaunaHumidifier(HumidifierEntity):
    """Humidifier entity class."""

    entity_description = HumidifierEntityDescription

    def __init__(self, hass, entry, description):
        """Initialize the device."""
        self.entity_description = description
        self._api = hass.data[DOMAIN][entry.entry_id]
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, "4321")})
        self._attr_unique_id = self.entity_description.key
        self._attr_has_entity_name = True
        self._attr_should_poll = False

        self._attr_supported_modes = HumidifierEntityFeature.MODES
        self._attr_mode = MODE_NORMAL

    async def async_added_to_hass(self):
        """Register callbacks."""
        async_dispatcher_connect(self.hass, SIGNAL_UPDATE_SENTIO, self._update_callback)

    @callback
    def _update_callback(self):
        """Call update method."""
        self.async_schedule_update_ha_state(True)

    @property
    def is_on(self):
        return self._api.steam

    @property
    def target_humidity(self):
        return self._api.steam_val

    @property
    def mode(self):
        return MODE_NORMAL

    async def async_turn_on(self, **kwargs):
        """Turn vaporizer on."""
        self._api.set_steam(PYS_STATE_ON)
        self.async_update_ha_state(True)
        dispatcher_send(self.hass, SIGNAL_UPDATE_SENTIO)

    async def async_turn_off(self, **kwargs):
        """Turn vaporizer off."""
        self._api.set_steam(PYS_STATE_OFF)
        self.async_update_ha_state(True)
        dispatcher_send(self.hass, SIGNAL_UPDATE_SENTIO)

    async def async_set_humidity(self, humidity):
        """Set new target humidity."""
        self._api.set_steam_val(int(humidity))
        return

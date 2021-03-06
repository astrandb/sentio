"""Light component for Sentio sauna controller"""

import logging

from homeassistant.components.light import SUPPORT_BRIGHTNESS, LightEntity

# from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from pysentio import PYS_STATE_OFF, PYS_STATE_ON

from .const import DOMAIN, MANUFACTURER, SIGNAL_UPDATE_SENTIO

# from collections import OrderedDict


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    def get_lights():
        return [SaunaLight(hass, entry)]

    async_add_entities(await hass.async_add_job(get_lights), True)


class SaunaLight(LightEntity):
    """Representation of a light."""

    def __init__(self, hass, entry):
        """Initialize the sensor."""
        self._entryid = entry.entry_id
        self._api = hass.data[DOMAIN][entry.entry_id]
        self._unique_id = DOMAIN + "_" + "saunalight"

    @property
    def device_info(self):
        return {
            "config_entry_id": self._entryid,
            "connections": {(DOMAIN, "4322")},
            "identifiers": {(DOMAIN, "4321")},
            "manufacturer": MANUFACTURER,
            "model": "Pro {}".format(self._api.type),
            "name": "Sauna controller",
            "sw_version": self._api.sw_version,
        }

    @property
    def should_poll(self):
        return False

    async def async_added_to_hass(self):
        """Register callbacks."""
        async_dispatcher_connect(self.hass, SIGNAL_UPDATE_SENTIO, self._update_callback)

    @callback
    def _update_callback(self):
        """Call update method."""
        _LOGGER.debug(self.name + " update_callback state: %s", self._api.light_is_on)
        self.async_schedule_update_ha_state(True)

    @property
    def name(self):
        """Return the name of the light."""
        return "Sauna Light"

    @property
    def unique_id(self):
        """Return the ID of this device."""
        return self._unique_id

    @property
    def supported_features(self):
        feat = 0
        if self._api.config("light dimming") == "on":
            feat = feat | SUPPORT_BRIGHTNESS
        return feat

    @property
    def is_on(self):
        return self._api.light_is_on

    async def async_turn_on(self, **kwargs):
        _LOGGER.debug(self.name + " Turn_on")
        self._api.set_light(PYS_STATE_ON)
        self.async_schedule_update_ha_state(True)

    async def async_turn_off(self, **kwargs):
        _LOGGER.debug(self.name + " Turn_off")
        self._api.set_light(PYS_STATE_OFF)
        self.async_schedule_update_ha_state(True)

    @property
    def brightness(self):
        return int(50 * 2.55)

    async def async_update(self):
        return

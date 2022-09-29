import logging

from homeassistant.components.switch import SwitchEntity

# from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect, dispatcher_send
from homeassistant.helpers.entity import DeviceInfo
from pysentio import PYS_STATE_OFF, PYS_STATE_ON

from .const import DOMAIN, SIGNAL_UPDATE_SENTIO

# from collections import OrderedDict


_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    return


async def async_setup_entry(hass, entry, async_add_entities):
    def get_entities():
        return [SaunaOn(hass, entry)]

    async_add_entities(await hass.async_add_job(get_entities), True)


class SaunaOn(SwitchEntity):
    """Representation of a switch."""

    def __init__(self, hass, entry):
        """Initialize the sensor."""
        self._entryid = entry.entry_id
        self._attr_unique_id = "sauna_switch"
        self._attr_has_entity_name = True
        self._attr_should_poll = False
        self._attr_name = "Heater"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, "4321")})
        self._attr_icon = "mdi:radiator"
        self._api = hass.data[DOMAIN][entry.entry_id]

    async def async_added_to_hass(self):
        """Register callbacks."""
        async_dispatcher_connect(self.hass, SIGNAL_UPDATE_SENTIO, self._update_callback)

    @callback
    def _update_callback(self):
        """Call update method."""
        _LOGGER.debug(self.name + " update_callback state: %s", self._api.is_on)
        self.async_schedule_update_ha_state(True)

    @property
    def is_on(self):
        return self._api.is_on

    async def async_turn_on(self, **kwargs):
        _LOGGER.debug(self.name + " Turn_on")
        self._api.set_sauna(PYS_STATE_ON)
        self.async_schedule_update_ha_state(True)
        dispatcher_send(self.hass, SIGNAL_UPDATE_SENTIO)

    async def async_turn_off(self, **kwargs):
        _LOGGER.debug(self.name + " Turn_off")
        self._api.set_sauna(PYS_STATE_OFF)
        self.async_schedule_update_ha_state(True)
        dispatcher_send(self.hass, SIGNAL_UPDATE_SENTIO)

    async def async_update(self):
        _LOGGER.debug(self.name + " Switch async_update 1 %s", self._api.is_on)

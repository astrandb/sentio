import logging
from collections import OrderedDict

from homeassistant.helpers.dispatcher import async_dispatcher_connect, dispatcher_send
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import callback
from .const import DOMAIN, MANUFACTURER, SIGNAL_UPDATE_SENTIO
from pysentio import PYS_STATE_OFF, PYS_STATE_ON

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
        self._unique_id = DOMAIN + '_' + 'sauna_on'
        self._api = hass.data[DOMAIN][entry.entry_id]

    @property
    def should_poll(self):
        return False

    async def async_added_to_hass(self):
        """Register callbacks."""
        async_dispatcher_connect(self.hass, SIGNAL_UPDATE_SENTIO, self._update_callback)

    @callback
    def _update_callback(self):
        """Call update method."""
        _LOGGER.debug(self.name + " update_callback state: %s", self._api.is_on)
        self.async_schedule_update_ha_state(True)

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Sauna'

    @property
    def device_info(self):
        return {
            "config_entry_id": self._entryid,
            "connections": {(DOMAIN, '4322')},
            "identifiers": {(DOMAIN, '4321')},
            "manufacturer": MANUFACTURER,
            "model": 'Pro {}'.format(self._api.type),
            "name": 'Sauna controller',
            "sw_version": self._api.sw_version,
        }

    @property
    def unique_id(self):
        """Return the ID of this device."""
        return self._unique_id

    @property
    def icon(self):
        return 'mdi:radiator'

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


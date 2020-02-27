import logging
from collections import OrderedDict

from homeassistant.helpers.dispatcher import async_dispatcher_connect, dispatcher_send
from homeassistant.helpers.entity import Entity
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.components.switch import SwitchDevice
from homeassistant.core import callback
from . import DOMAIN, SIGNAL_UPDATE_SENTIO
from pysentio import SentioPro

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    # We only want this platform to be set up via discovery.
    if discovery_info is None:
        return
    add_entities([SaunaOn(hass)])


class SaunaOn(SwitchDevice):
    """Representation of a switch."""

    def __init__(self, hass):
        """Initialize the sensor."""
        self._hassdd = hass.data[DOMAIN]['sentio']
        self._unique_id = DOMAIN + '_' + 'sauna_on'
    
    @property
    def should_poll(self):
        return False

    async def async_added_to_hass(self):
        """Register callbacks."""
        async_dispatcher_connect(self.hass, SIGNAL_UPDATE_SENTIO, self._update_callback)

    @callback
    def _update_callback(self):
        """Call update method."""
        _LOGGER.debug(self.name + " update_callback state: %s", self._hassdd.is_on)
        self.async_schedule_update_ha_state(True)

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Sauna'

    @property
    def unique_id(self):
        """Return the ID of this device."""
        return self._unique_id

    @property
    def icon(self):
        return 'mdi:radiator'

    @property
    def is_on(self):
        return self._hassdd.is_on

    async def async_turn_on(self, **kwargs):
        _LOGGER.debug(self.name + " Turn_on")
        self._hassdd.set_sauna(STATE_ON)
        self.async_schedule_update_ha_state(True)
        dispatcher_send(self.hass, SIGNAL_UPDATE_SENTIO)

    async def async_turn_off(self, **kwargs):
        _LOGGER.debug(self.name + " Turn_off")
        self._hassdd.set_sauna(STATE_OFF)
        self.async_schedule_update_ha_state(True)
        dispatcher_send(self.hass, SIGNAL_UPDATE_SENTIO)

    async def async_update(self):
        return

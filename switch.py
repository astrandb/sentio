import logging
from collections import OrderedDict

from homeassistant.helpers.entity import Entity
from homeassistant.components.switch import SwitchDevice
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    # We only want this platform to be set up via discovery.
    if discovery_info is None:
        return
    add_entities([SaunaOn(), SaunaLightOn()])


class SaunaOn(SwitchDevice):
    """Representation of a switch."""

    def __init__(self):
        """Initialize the sensor."""
        self._unique_id = DOMAIN + '_' + 'sauna_on'
        self._state = None

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
        return self._state

    @property
    def device_state_attributes(self):
        """Return extra state."""
        data = OrderedDict()
        data['Attr1'] = 11
        data['Attr2'] = 'Twentytwoo'
        return data

    async def async_turn_on(self, **kwargs):
        _LOGGER.debug(self.name + " Turn_on")
        self.hass.data[DOMAIN]['sauna_on'] = True

    async def async_turn_off(self, **kwargs):
        _LOGGER.debug(self.name + " Turn_off")
        self.hass.data[DOMAIN]['sauna_on'] = False

    def update(self):
        """Fetch new state data for this switch.
        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = self.hass.data[DOMAIN]['sauna_on']

class SaunaLightOn(SwitchDevice):
    """Representation of a switch."""

    def __init__(self):
        """Initialize the sensor."""
        self._unique_id = DOMAIN + '_' + 'sauna_light_on'
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Sauna Light'

    @property
    def unique_id(self):
        """Return the ID of this device."""
        return self._unique_id

    @property
    def icon(self):
        return 'mdi:lightbulb'

    @property
    def is_on(self):
        return self._state

    async def async_turn_on(self, **kwargs):
        _LOGGER.debug(self.name + " Turn_on")
        self.hass.data[DOMAIN]['sauna_light_on'] = True

    async def async_turn_off(self, **kwargs):
        _LOGGER.debug(self.name + " Turn_off")
        self.hass.data[DOMAIN]['sauna_light_on'] = False

    def update(self):
        """Fetch new state data for this switch.
        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = self.hass.data[DOMAIN]['sauna_light_on']

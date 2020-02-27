"""Platform for sensor integration."""
import logging
from homeassistant.const import (
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_TEMPERATURE,
    TEMP_CELSIUS,
)
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

from . import DOMAIN, SIGNAL_UPDATE_SENTIO

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    # We only want this platform to be set up via discovery.
    if discovery_info is None:
        return
    add_entities([BenchSensor(hass), HeaterSensor(hass)])


class BenchSensor(Entity):
    """Representation of a sensor."""

    def __init__(self, hass):
        """Initialize the sensor."""
        self._unique_id = DOMAIN + '_' + 'bench_sensor'
        self._hassdd = hass.data[DOMAIN]['sentio']

    async def async_added_to_hass(self):
        """Register callbacks."""
        async_dispatcher_connect(self.hass, SIGNAL_UPDATE_SENTIO, self._update_callback)

    @callback
    def _update_callback(self):
        """Call update method."""
        _LOGGER.debug(self.name + " update_callback state: %s", self._hassdd.bench_temperature)
        self.async_schedule_update_ha_state(True)

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Sauna Bench'

    @property
    def unique_id(self):
        """Return the ID of this device."""
        return self._unique_id
    
    @property
    def should_poll(self):
        return False

    @property
    def state(self):
        """Return the state of the sensor."""
        return  self._hassdd.bench_temperature

    @property
    def device_class(self):
        return DEVICE_CLASS_TEMPERATURE

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    async def async_update(self):
        _LOGGER.debug(self.name + " async_update 1 %s", self._hassdd.bench_temperature)

class HeaterSensor(Entity):
    """Representation of a sensor."""

    def __init__(self, hass):
        """Initialize the sensor."""
        self._unique_id = DOMAIN + '_' + 'heater_sensor'
        self._hassdd = hass.data[DOMAIN]['sentio']

    async def async_added_to_hass(self):
        """Register callbacks."""
        async_dispatcher_connect(self.hass, SIGNAL_UPDATE_SENTIO, self._update_callback)

    @callback
    def _update_callback(self):
        """Call update method."""
        _LOGGER.debug(self.name + " update_callback state: %s", self._hassdd.heater_temperature)
        self.async_schedule_update_ha_state(True)

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Sauna Heater'

    @property
    def unique_id(self):
        """Return the ID of this device."""
        return self._unique_id

    @property
    def should_poll(self):
        return False

    @property
    def state(self):
        """Return the state of the sensor."""
        # self._state = self._hassdd.heater_temp
        return  self._hassdd.heater_temperature

    @property
    def device_class(self):
        return DEVICE_CLASS_TEMPERATURE
        
    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    async def async_update(self):
        _LOGGER.debug(self.name + " async_update 1 %s", self._hassdd.heater_temperature)
        return

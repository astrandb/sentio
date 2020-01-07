"""Platform for sensor integration."""
import logging
from homeassistant.const import TEMP_CELSIUS
from homeassistant.helpers.entity import Entity

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    # We only want this platform to be set up via discovery.
    if discovery_info is None:
        return
    add_entities([BenchSensor(), HeaterSensor()])


class BenchSensor(Entity):
    """Representation of a sensor."""

    def __init__(self):
        """Initialize the sensor."""
        self._unique_id = DOMAIN + '_' + 'bench_sensor'
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Sauna Bench'

    @property
    def unique_id(self):
        """Return the ID of this device."""
        return self._unique_id

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        Körs var 30:e sek som default
        """
        _LOGGER.debug("Updating Bench temp sensor");
        self._state = self.hass.data[DOMAIN]['bench_temperature']

class HeaterSensor(Entity):
    """Representation of a sensor."""

    def __init__(self):
        """Initialize the sensor."""
        self._unique_id = DOMAIN + '_' + 'heater_sensor'
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Sauna Heater'

    @property
    def unique_id(self):
        """Return the ID of this device."""
        return self._unique_id

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = self.hass.data[DOMAIN]['heater_temperature']
"""Platform for sensor integration."""
import logging
import re

from homeassistant.const import (
    CONF_DEVICE_CLASS,
    CONF_NAME,
    CONF_UNIT_OF_MEASUREMENT,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_TEMPERATURE,
    TEMP_CELSIUS,
)
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, MANUFACTURER, SIGNAL_UPDATE_SENTIO

_LOGGER = logging.getLogger(__name__)

ATTR_HEATER_TEMP = "heater_temp"
ATTR_BENCH_TEMP = "bench_temp"
ATTR_FOIL_TEMP = "foil_temp"
ATTR_HUMIDITY = "humidity"


SENSOR_TYPES = {
    ATTR_HEATER_TEMP: {
        CONF_NAME: "Sauna Heater",
        CONF_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
        CONF_UNIT_OF_MEASUREMENT: TEMP_CELSIUS,
    },
    ATTR_BENCH_TEMP: {
        CONF_NAME: "Sauna Bench",
        CONF_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
        CONF_UNIT_OF_MEASUREMENT: TEMP_CELSIUS,
    },
    ATTR_FOIL_TEMP: {
        CONF_NAME: "Sauna Foil",
        CONF_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
        CONF_UNIT_OF_MEASUREMENT: TEMP_CELSIUS,
    },
    ATTR_HUMIDITY: {
        CONF_NAME: "Sauna Humidity",
        CONF_DEVICE_CLASS: DEVICE_CLASS_HUMIDITY,
        CONF_UNIT_OF_MEASUREMENT: "%",
    },
}


# def setup_platform(hass, config, add_entities, discovery_info=None):
#     """Set up the sensor platform."""
#     # We only want this platform to be set up via discovery.
#     # if discovery_info is None:
#     #     return
#     # add_entities([BenchSensor(hass), HeaterSensor(hass)])
#     return


async def async_setup_entry(hass, entry, async_add_entities):
    def get_entities():
        api = hass.data[DOMAIN][entry.entry_id]
        sensors = [HeaterSensor(hass, entry)]
        if api.config("sens bench") == "on":
            sensors.append(BenchSensor(hass, entry))
        if re.match("D3", api.type):
            sensors.append(HumiditySensor(hass, entry))
        return sensors

    async_add_entities(await hass.async_add_job(get_entities), True)


class BenchSensor(Entity):
    """Representation of a sensor."""

    def __init__(self, hass, entry):
        """Initialize the sensor."""
        self._entryid = entry.entry_id
        self._unique_id = DOMAIN + "_" + "bench_sensor"
        self._api = hass.data[DOMAIN][entry.entry_id]

    async def async_added_to_hass(self):
        """Register callbacks."""
        async_dispatcher_connect(self.hass, SIGNAL_UPDATE_SENTIO, self._update_callback)

    @callback
    def _update_callback(self):
        """Call update method."""
        _LOGGER.debug(
            self.name + " update_callback state: %s", self._api.bench_temperature
        )
        self.async_schedule_update_ha_state(True)

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Sauna Bench"

    @property
    def unique_id(self):
        """Return the ID of this device."""
        return self._unique_id

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

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._api.bench_temperature

    @property
    def device_class(self):
        return DEVICE_CLASS_TEMPERATURE

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    async def async_update(self):
        _LOGGER.debug(self.name + " async_update 1 %s", self._api.bench_temperature)
        return


class HeaterSensor(Entity):
    """Representation of a sensor."""

    def __init__(self, hass, entry):
        """Initialize the sensor."""
        self._entryid = entry.entry_id
        self._unique_id = DOMAIN + "_" + "heater_sensor"
        self._api = hass.data[DOMAIN][entry.entry_id]

    async def async_added_to_hass(self):
        """Register callbacks."""
        async_dispatcher_connect(self.hass, SIGNAL_UPDATE_SENTIO, self._update_callback)

    @callback
    def _update_callback(self):
        """Call update method."""
        _LOGGER.debug(
            self.name + " update_callback state: %s", self._api.heater_temperature
        )
        self.async_schedule_update_ha_state(True)

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Sauna Heater"

    @property
    def unique_id(self):
        """Return the ID of this device."""
        return self._unique_id

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

    @property
    def state(self):
        """Return the state of the sensor."""
        # self._state = self._api.heater_temp
        return self._api.heater_temperature

    @property
    def device_class(self):
        return DEVICE_CLASS_TEMPERATURE

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    async def async_update(self):
        _LOGGER.debug(self.name + " async_update 1 %s", self._api.heater_temperature)
        return


class HumiditySensor(Entity):
    """Representation of a sensor."""

    def __init__(self, hass, entry):
        """Initialize the sensor."""
        self._entryid = entry.entry_id
        self._unique_id = DOMAIN + "_" + "humidity_sensor"
        self._api = hass.data[DOMAIN][entry.entry_id]

    async def async_added_to_hass(self):
        """Register callbacks."""
        async_dispatcher_connect(self.hass, SIGNAL_UPDATE_SENTIO, self._update_callback)

    @callback
    def _update_callback(self):
        """Call update method."""
        _LOGGER.debug(self.name + " update_callback state: %s", self._api.humidity)
        self.async_schedule_update_ha_state(True)

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Sauna Humidity"

    @property
    def unique_id(self):
        """Return the ID of this device."""
        return self._unique_id

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

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._api.humidity

    @property
    def device_class(self):
        return DEVICE_CLASS_HUMIDITY

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "%"

    async def async_update(self):
        _LOGGER.debug(self.name + " async_update 1 %s", self._api.humidity)
        return

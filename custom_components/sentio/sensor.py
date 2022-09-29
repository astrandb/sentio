"""Platform for sensor integration."""
import logging
import re

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import TEMP_CELSIUS
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, SIGNAL_UPDATE_SENTIO

_LOGGER = logging.getLogger(__name__)


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


class BenchSensor(SensorEntity):
    """Representation of a sensor."""

    def __init__(self, hass, entry):
        """Initialize the sensor."""
        self._entryid = entry.entry_id
        self._api = hass.data[DOMAIN][entry.entry_id]
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, "4321")})
        self._attr_should_poll = False
        self._attr_unique_id = "sauna_bench_sensor"
        self._attr_has_entity_name = True
        self._attr_name = "Bench"
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = TEMP_CELSIUS

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
    def native_value(self):
        """Return the state of the sensor."""
        return self._api.bench_temperature

    async def async_update(self):
        _LOGGER.debug(self.name + " async_update 1 %s", self._api.bench_temperature)
        return


class HeaterSensor(SensorEntity):
    """Representation of a sensor."""

    def __init__(self, hass, entry):
        """Initialize the sensor."""
        self._entryid = entry.entry_id
        self._api = hass.data[DOMAIN][entry.entry_id]
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, "4321")})
        self._attr_should_poll = False
        self._attr_unique_id = "sauna_heater_sensor"
        self._attr_has_entity_name = True
        self._attr_name = "Heater"
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = TEMP_CELSIUS

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
    def native_value(self):
        """Return the state of the sensor."""
        # self._state = self._api.heater_temp
        return self._api.heater_temperature

    async def async_update(self):
        _LOGGER.debug(self.name + " async_update 1 %s", self._api.heater_temperature)
        return


class HumiditySensor(SensorEntity):
    """Representation of a sensor."""

    def __init__(self, hass, entry):
        """Initialize the sensor."""
        self._entryid = entry.entry_id
        self._api = hass.data[DOMAIN][entry.entry_id]
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, "4321")})
        self._attr_should_poll = False
        self._attr_unique_id = "sauna_humidity_sensor"
        self._attr_has_entity_name = True
        self._attr_name = "Humidity"
        self._attr_device_class = SensorDeviceClass.HUMIDITY
        self._attr_state_class = SensorStateClass.MEASUREMENT

    async def async_added_to_hass(self):
        """Register callbacks."""
        async_dispatcher_connect(self.hass, SIGNAL_UPDATE_SENTIO, self._update_callback)

    @callback
    def _update_callback(self):
        """Call update method."""
        _LOGGER.debug(self.name + " update_callback state: %s", self._api.humidity)
        self.async_schedule_update_ha_state(True)

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._api.humidity

    async def async_update(self):
        _LOGGER.debug(self.name + " async_update 1 %s", self._api.humidity)
        return

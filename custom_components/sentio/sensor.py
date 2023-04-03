"""Platform for sensor integration."""
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo, EntityCategory

from .const import DOMAIN, HUMIDITY_MODELS, SIGNAL_UPDATE_SENTIO

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup the sensor entities."""

    def get_entities():
        api = hass.data[DOMAIN][entry.entry_id]
        sensors = [SentioSensor(hass, entry, heater_temp_desc)]
        sensors.append(SentioSensor(hass, entry, timer_desc))
        sensors.append(SentioSensor(hass, entry, heat_timer_desc))
        if api.config("sens bench") == "on":
            sensors.append(SentioSensor(hass, entry, bench_temp_desc))
        if api.config("sens foil") == "on":
            sensors.append(SentioSensor(hass, entry, foil_temp_desc))
        if api.type.upper() in HUMIDITY_MODELS:
            sensors.append(SentioSensor(hass, entry, humidity_desc))
        return sensors

    async_add_entities(await hass.async_add_job(get_entities), True)


timer_desc = SensorEntityDescription(
    key="preset_timer",
    device_class=SensorDeviceClass.DURATION,
    entity_category=EntityCategory.DIAGNOSTIC,
    has_entity_name=True,
    translation_key="preset_timer",
    native_unit_of_measurement=UnitOfTime.MINUTES,
)

heat_timer_desc = SensorEntityDescription(
    key="heater_timer",
    device_class=SensorDeviceClass.DURATION,
    entity_category=EntityCategory.DIAGNOSTIC,
    has_entity_name=True,
    translation_key="heater_timer",
    native_unit_of_measurement=UnitOfTime.MINUTES,
)

foil_temp_desc = SensorEntityDescription(
    key="foil_temp",
    device_class=SensorDeviceClass.TEMPERATURE,
    has_entity_name=True,
    translation_key="foil_temp",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    state_class=SensorStateClass.MEASUREMENT,
)


heater_temp_desc = SensorEntityDescription(
    key="heater_temp",
    device_class=SensorDeviceClass.TEMPERATURE,
    has_entity_name=True,
    translation_key="heater_temp",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    state_class=SensorStateClass.MEASUREMENT,
)


bench_temp_desc = SensorEntityDescription(
    key="bench_temp",
    device_class=SensorDeviceClass.TEMPERATURE,
    has_entity_name=True,
    translation_key="bench_temp",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    state_class=SensorStateClass.MEASUREMENT,
)

humidity_desc = SensorEntityDescription(
    key="humidity",
    device_class=SensorDeviceClass.HUMIDITY,
    has_entity_name=True,
    translation_key="humidity",
    native_unit_of_measurement=PERCENTAGE,
    state_class=SensorStateClass.MEASUREMENT,
)


class SentioSensor(SensorEntity):
    """Class for Sentio sensors."""

    entity_description: SensorEntityDescription

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        description: SensorEntityDescription,
    ):
        self.entity_description = description
        self._attr_should_poll = False
        self._api = hass.data[DOMAIN][entry.entry_id]
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, "4321")})
        self._attr_unique_id = self.entity_description.key

    @property
    def native_value(self):
        if self.entity_description.key == "preset_timer":
            return self._api.timer_val
        if self.entity_description.key == "heater_timer":
            return self._api.heattimer_val
        if self.entity_description.key == "foil_temp":
            return self._api.foil_temperature
        if self.entity_description.key == "bench_temp":
            return self._api.bench_temperature
        if self.entity_description.key == "heater_temp":
            return self._api.heater_temperature
        if self.entity_description.key == "humidity":
            return self._api.humidity
        return None

    async def async_added_to_hass(self):
        """Register callbacks."""
        async_dispatcher_connect(self.hass, SIGNAL_UPDATE_SENTIO, self._update_callback)

    @callback
    def _update_callback(self):
        """Call update method."""
        _LOGGER.debug("%s update_callback state: %s", self.name, self._api.is_on)
        self.async_schedule_update_ha_state(True)

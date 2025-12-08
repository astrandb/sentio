"""Platform for sensor integration."""

import logging

from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import SentioConfigEntry
from .const import DOMAIN, HEATER_POWER, HUMIDITY_MODELS, SIGNAL_UPDATE_SENTIO

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SentioConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the sensor entities."""

    def get_entities() -> list[SentioSensor]:
        _api = entry.runtime_data.client
        sensors = [SentioSensor(hass, entry, heater_temp_desc)]
        sensors.append(SentioSensor(hass, entry, timer_desc))
        sensors.append(SentioSensor(hass, entry, heat_timer_desc))
        if _api.config("sens bench") == "on":
            sensors.append(SentioSensor(hass, entry, bench_temp_desc))
        if _api.config("sens foil") == "on":
            sensors.append(SentioSensor(hass, entry, foil_temp_desc))
        if _api.type.upper() in HUMIDITY_MODELS:
            sensors.append(SentioSensor(hass, entry, humidity_desc))
        if entry.data.get(HEATER_POWER, 0) > 0:
            sensors.append(SentioSensor(hass, entry, heater_power_desc))
            sensors.append(SentioRestoreSensor(hass, entry, heater_energy_desc))
        return sensors

    async_add_entities(get_entities())


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

heater_power_desc = SensorEntityDescription(
    key="heater_power",
    device_class=SensorDeviceClass.POWER,
    has_entity_name=True,
    native_unit_of_measurement=UnitOfPower.KILO_WATT,
    suggested_display_precision=1,
    state_class=SensorStateClass.MEASUREMENT,
)

heater_energy_desc = SensorEntityDescription(
    key="heater_energy",
    device_class=SensorDeviceClass.ENERGY,
    has_entity_name=True,
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    state_class=SensorStateClass.TOTAL_INCREASING,
)


class SentioSensor(SensorEntity):
    """Class for Sentio sensors."""

    entity_description: SensorEntityDescription

    def __init__(
        self,
        hass: HomeAssistant,
        entry: SentioConfigEntry,
        description: SensorEntityDescription,
    ):
        """Init the SentioSensor class."""

        self.entry = entry
        self.entity_description = description
        self._attr_should_poll = False
        self._api = entry.runtime_data.client
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, "4321")})
        self._attr_unique_id = self.entity_description.key
        self.heater_energy = 0
        self._attr_native_value = 0

    @property
    def native_value(self) -> float | int | None:
        """Return native value."""
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
        if self.entity_description.key == "heater_power":
            return (
                self.entry.data.get(HEATER_POWER, 0)
                if self._api.is_on
                and (self._api.heater_temperature < self._api.target_temperature)
                else 0
            )
        return None

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        async_dispatcher_connect(self.hass, SIGNAL_UPDATE_SENTIO, self._update_callback)

    @callback
    def _update_callback(self):
        """Call update method."""
        _LOGGER.debug("%s update_callback state: %s", self.name, self._api.is_on)
        self.async_schedule_update_ha_state(True)


class SentioRestoreSensor(SentioSensor, RestoreSensor):
    """Class for Sentio sensors that restore state."""

    heater_energy = 0.0

    @property
    def native_value(self) -> float | None:
        """Return native value."""
        return self._attr_native_value

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        await super().async_added_to_hass()
        if (last_sensor_data := await self.async_get_last_sensor_data()) is not None:
            self._attr_native_value = self.heater_energy = last_sensor_data.native_value

    def _update_native_value(self) -> None:
        """Update the native value attribute of the sensor."""
        native_value = None
        if self.entity_description.key == "heater_energy":
            self.heater_energy += (
                (self.entry.data.get(HEATER_POWER, 0) / 60.0)
                if self._api.is_on
                and (self._api.heater_temperature < self._api.target_temperature)
                else 0.0
            )
            native_value = self.heater_energy

        self._attr_native_value = native_value

    @callback
    def _update_callback(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_native_value()
        super()._update_callback()

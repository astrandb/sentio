"""Climate component for Sentio sauna controller."""

import logging

from pysentio import PYS_STATE_OFF, PYS_STATE_ON

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, PRECISION_WHOLE, UnitOfTemperature
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect, dispatcher_send
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, MAX_SET_TEMP, MIN_SET_TEMP, SIGNAL_UPDATE_SENTIO

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the climate entities."""

    def get_climates():
        return [SaunaClimate(hass, entry)]

    async_add_entities(await hass.async_add_job(get_climates), True)


class SaunaClimate(ClimateEntity):
    """Climate entity class."""

    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TURN_ON
    )
    _attr_target_temperature_step = 1.0
    _enable_turn_on_off_backwards_compatibility = False

    def __init__(self, hass, entry):
        """Initialize the device."""
        self._entryid = entry.entry_id
        self._api = hass.data[DOMAIN][entry.entry_id]
        self._attr_unique_id = "sauna_climate"
        self._attr_has_entity_name = True
        self._attr_should_poll = False
        self._attr_name = None
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, "4321")})

        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_min_temp = MIN_SET_TEMP
        self._attr_precision = PRECISION_WHOLE

    async def async_added_to_hass(self):
        """Register callbacks."""
        async_dispatcher_connect(self.hass, SIGNAL_UPDATE_SENTIO, self._update_callback)

    @callback
    def _update_callback(self):
        """Call update method."""
        _LOGGER.debug("Sauna climate update_callback state: %s", self._api.hvac_mode)
        self.async_schedule_update_ha_state(True)

    @property
    def max_temp(self):
        """Return max set temp."""
        return min(MAX_SET_TEMP, int(self._api.config("max preset temp")))

    @property
    def hvac_mode(self):
        """Return hvac mode."""
        return self._api.hvac_mode

    @property
    def hvac_action(self):
        """Return hvac action."""
        if self.hvac_mode == HVACMode.OFF:
            return HVACAction.OFF
        if self.current_temperature < self.target_temperature:
            return HVACAction.HEATING
        return HVACAction.IDLE

    @property
    def current_temperature(self):
        """Return current temperature."""
        return self._api.bench_temperature

    @property
    def target_temperature(self):
        """Return target temperature."""
        return self._api.target_temperature

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        _LOGGER.debug("Sauna hvac_mode = %s", hvac_mode)
        if hvac_mode == HVACMode.HEAT:
            self._api.set_sauna(PYS_STATE_ON)
        else:
            self._api.set_sauna(PYS_STATE_OFF)
        await self.async_update_ha_state(True)
        dispatcher_send(self.hass, SIGNAL_UPDATE_SENTIO)

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        temp = kwargs.get(ATTR_TEMPERATURE)
        self._api.set_sauna_val(int(temp))
        _LOGGER.debug("Sauna New target temp => %s", temp)

    async def async_update(self):
        """Update climate entity."""
        _LOGGER.debug("Sauna climate async_update 1 %s", self._api.hvac_mode)

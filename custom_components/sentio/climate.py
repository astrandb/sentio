"""Climate component for Sentio sauna controller"""

import logging

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE,
    CURRENT_HVAC_OFF,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect, dispatcher_send
from homeassistant.helpers.entity import DeviceInfo
from pysentio import PYS_STATE_OFF, PYS_STATE_ON

from .const import DOMAIN, MAX_SET_TEMP, MIN_SET_TEMP, SIGNAL_UPDATE_SENTIO

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    def get_climates():
        return [SaunaClimate(hass, entry)]

    async_add_entities(await hass.async_add_job(get_climates), True)


class SaunaClimate(ClimateEntity):
    def __init__(self, hass, entry):
        """Initialize the device."""
        self._entryid = entry.entry_id
        self._api = hass.data[DOMAIN][entry.entry_id]
        self._attr_unique_id = "sauna_climate"
        self._attr_has_entity_name = True
        self._attr_should_poll = False
        self._attr_name = None
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, "4321")})

        self._attr_temperature_unit = TEMP_CELSIUS
        self._attr_min_temp = MIN_SET_TEMP
        self._attr_precision = 1.0
        self._attr_hvac_modes = [HVAC_MODE_OFF, HVAC_MODE_HEAT]
        self._attr_supported_features = SUPPORT_TARGET_TEMPERATURE
        self._attr_target_temperature_step = 1.0

    async def async_added_to_hass(self):
        """Register callbacks."""
        async_dispatcher_connect(self.hass, SIGNAL_UPDATE_SENTIO, self._update_callback)

    @callback
    def _update_callback(self):
        """Call update method."""
        _LOGGER.debug(
            "Sauna" + " climate update_callback state: %s", self._api.hvac_mode
        )
        self.async_schedule_update_ha_state(True)

    @property
    def max_temp(self):
        return min(MAX_SET_TEMP, int(self._api.config("max preset temp")))

    @property
    def hvac_mode(self):
        return self._api.hvac_mode

    @property
    def hvac_action(self):
        if self.hvac_mode == HVAC_MODE_OFF:
            return CURRENT_HVAC_OFF
        if self.current_temperature < self.target_temperature:
            return CURRENT_HVAC_HEAT
        return CURRENT_HVAC_IDLE

    @property
    def current_temperature(self):
        return self._api.bench_temperature

    @property
    def target_temperature(self):
        return self._api.target_temperature

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        _LOGGER.debug("Sauna" + " hvac_mode = %s", hvac_mode)
        if hvac_mode == HVAC_MODE_HEAT:
            self._api.set_sauna(PYS_STATE_ON)
        else:
            self._api.set_sauna(PYS_STATE_OFF)
        self.async_update_ha_state(True)
        dispatcher_send(self.hass, SIGNAL_UPDATE_SENTIO)

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        temp = kwargs.get(ATTR_TEMPERATURE)
        self._api.set_sauna_val(int(temp))
        _LOGGER.debug("Sauna" + " New target temp => %s", temp)
        return

    async def async_update(self):
        _LOGGER.debug("Sauna" + "climate async_update 1 %s", self._api.hvac_mode)
        return

"""Climate component for Sentio sauna controller."""

import logging

from pysentio import PYS_STATE_OFF, PYS_STATE_ON

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityDescription,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, PRECISION_WHOLE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import SentioConfigEntry
from .const import MAX_SET_TEMP, MIN_SET_TEMP, SIGNAL_UPDATE_SENTIO
from .entity import SentioEntity

_LOGGER = logging.getLogger(__name__)

CLIMATE_DESCR = ClimateEntityDescription(
    key="sauna_climate",
    name=None,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SentioConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the climate entities."""

    def get_climates() -> list[SaunaClimate]:
        return [SaunaClimate(hass, entry, CLIMATE_DESCR)]

    async_add_entities(get_climates())


class SaunaClimate(SentioEntity, ClimateEntity):
    """Climate entity class."""

    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TURN_ON
    )
    _attr_target_temperature_step = 1.0
    _enable_turn_on_off_backwards_compatibility = False
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_min_temp = MIN_SET_TEMP
    _attr_precision = PRECISION_WHOLE

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

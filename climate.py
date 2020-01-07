import logging
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS
from homeassistant.helpers.entity import Entity
from homeassistant.components.climate import ClimateDevice
from homeassistant.components.climate.const import (CURRENT_HVAC_HEAT, CURRENT_HVAC_IDLE, CURRENT_HVAC_OFF,
                                          HVAC_MODE_HEAT, HVAC_MODE_OFF, SUPPORT_TARGET_TEMPERATURE)
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    # We only want this platform to be set up via discovery.
    if discovery_info is None:
        return
    add_entities([SaunaClimate()])


class SaunaClimate(ClimateDevice):

    def __init__(self):
        """Initialize the device."""
        self._unique_id = DOMAIN + '_' + 'climate'
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
    def temperature_unit(self):
        return TEMP_CELSIUS

    @property
    def min_temp(self):
        return 30

    @property
    def max_temp(self):
        return 110

    @property
    def precision(self):
        return 1.0

    @property
    def hvac_mode(self):
        return self.hass.data[DOMAIN]['hvac_mode']

    @property
    def hvac_action(self):
        return CURRENT_HVAC_OFF

    @property
    def current_temperature(self):
        return self.hass.data[DOMAIN]['bench_temperature']

    @property
    def target_temperature(self):
        return self.hass.data[DOMAIN]['target_temperature']

    @property
    def hvac_modes(self):
        return [HVAC_MODE_OFF, HVAC_MODE_HEAT]

    @property
    def supported_features(self):
        return SUPPORT_TARGET_TEMPERATURE

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        _LOGGER.debug(self.name + " hvac_mode = %s", hvac_mode)
        self.hass.data[DOMAIN]['hvac_mode'] = hvac_mode
        if hvac_mode == HVAC_MODE_HEAT:
            self.hass.data[DOMAIN]['sauna_on'] = True
        else:
            self.hass.data[DOMAIN]['sauna_on'] = False

        await self.async_update_ha_state()

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        temp = kwargs.get(ATTR_TEMPERATURE)
        _LOGGER.debug(self.name + " target temp = %s", temp)
        self.hass.data[DOMAIN]['target_temperature'] = temp


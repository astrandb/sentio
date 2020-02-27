import logging
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS, STATE_OFF, STATE_ON
from homeassistant.helpers.dispatcher import async_dispatcher_connect, dispatcher_send
from homeassistant.helpers.entity import Entity
from homeassistant.components.climate import ClimateDevice
from homeassistant.components.climate.const import (CURRENT_HVAC_HEAT, CURRENT_HVAC_IDLE, CURRENT_HVAC_OFF,
                                          HVAC_MODE_HEAT, HVAC_MODE_OFF, SUPPORT_TARGET_TEMPERATURE)
from homeassistant.core import callback
from . import DOMAIN, SIGNAL_UPDATE_SENTIO
from pysentio import SentioPro

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    # We only want this platform to be set up via discovery.
    if discovery_info is None:
        return
    add_entities([SaunaClimate(hass)])


class SaunaClimate(ClimateDevice):

    def __init__(self, hass):
        """Initialize the device."""
        self._unique_id = DOMAIN + '_' + 'climate'
        self._hassdd = hass.data[DOMAIN]['sentio']

    async def async_added_to_hass(self):
        """Register callbacks."""
        async_dispatcher_connect(self.hass, SIGNAL_UPDATE_SENTIO, self._update_callback)

    @callback
    def _update_callback(self):
        """Call update method."""
        _LOGGER.debug(self.name + " climate update_callback state: %s", self._hassdd.hvac_mode)
        self.async_schedule_update_ha_state(True)

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Sauna'

    @property
    def should_poll(self):
        return False

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
        return self._hassdd.hvac_mode

    # @property
    # def hvac_action(self):
    #     return CURRENT_HVAC_OFF

    @property
    def current_temperature(self):
        return self._hassdd.bench_temperature

    @property
    def target_temperature(self):
        return self._hassdd.target_temperature

    @property
    def target_temperature_step(self):
        return 1.0

    @property
    def hvac_modes(self):
        return [HVAC_MODE_OFF, HVAC_MODE_HEAT]

    @property
    def supported_features(self):
        return SUPPORT_TARGET_TEMPERATURE

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        _LOGGER.debug(self.name + " hvac_mode = %s", hvac_mode)
        if hvac_mode == HVAC_MODE_HEAT:
            self._hassdd.set_sauna(STATE_ON)
        else:
            self._hassdd.set_sauna(STATE_OFF)
        self.async_update_ha_state(True)
        dispatcher_send(self.hass, SIGNAL_UPDATE_SENTIO)

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        temp = kwargs.get(ATTR_TEMPERATURE)
        self._hassdd.set_sauna_val(int(temp))
        _LOGGER.debug(self.name + " New target temp => %s", temp)
        return

    async def async_update(self):
        _LOGGER.debug(self.name + "climate async_update 1 %s", self._hassdd.hvac_mode)

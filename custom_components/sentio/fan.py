import logging

from homeassistant.components.fan import SUPPORT_SET_SPEED, FanEntity

# from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo

# from homeassistant.helpers.entity import Entity
from pysentio import PYS_STATE_OFF, PYS_STATE_ON

from .const import DOMAIN, FAN_DISABLED, SIGNAL_UPDATE_SENTIO

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    def get_fans():
        sensors = []
        if not entry.data.get(FAN_DISABLED):
            sensors.append(SaunaFan(hass, entry))
        return sensors

    async_add_entities(await hass.async_add_job(get_fans), True)


class SaunaFan(FanEntity):
    """Representation of a fan."""

    def __init__(self, hass, entry):
        """Initialize the sensor."""
        self._entryid = entry.entry_id
        self._api = hass.data[DOMAIN][entry.entry_id]
        self._attr_unique_id = "sauna_fan"
        self._attr_has_entity_name = True
        self._attr_should_poll = False
        self._attr_name = "Fan"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, "4321")})

    async def async_added_to_hass(self):
        """Register callbacks."""
        async_dispatcher_connect(self.hass, SIGNAL_UPDATE_SENTIO, self._update_callback)

    @callback
    def _update_callback(self):
        """Call update method."""
        _LOGGER.debug(self.name + " update_callback state: %s", self._api.fan)
        self.async_schedule_update_ha_state(True)

    @property
    def supported_features(self):
        feat = 0
        if self._api.config("fan dimming") == "on":
            feat = feat | SUPPORT_SET_SPEED
        return feat

    @property
    def is_on(self):
        return self._api.fan

    async def async_turn_on(self, **kwargs):
        _LOGGER.debug(self.name + " Turn_on")
        self._api.set_fan(PYS_STATE_ON)
        self.async_schedule_update_ha_state(True)

    async def async_turn_off(self, **kwargs):
        _LOGGER.debug(self.name + " Turn_off")
        self._api.set_fan(PYS_STATE_OFF)
        self.async_schedule_update_ha_state(True)

    @property
    def percentage(self):
        return 0 if self._api.fan else 100

    async def async_update(self):
        return

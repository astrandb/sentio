"""Light component for Sentio sauna controller."""

import logging

from pysentio import PYS_STATE_OFF, PYS_STATE_ON

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import SentioConfigEntry
from .const import DOMAIN, SIGNAL_UPDATE_SENTIO

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SentioConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the entry."""

    def get_lights() -> list[SaunaLight]:
        return [SaunaLight(hass, entry)]

    async_add_entities(get_lights())


class SaunaLight(LightEntity):
    """Representation of a light."""

    def __init__(self, hass: HomeAssistant, entry: SentioConfigEntry):
        """Initialize the light entity."""
        self._api = entry.runtime_data.client
        self._attr_unique_id = "sauna_light"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, "4321")})
        self._attr_should_poll = False
        self._attr_translation_key = "light"
        self._attr_has_entity_name = True
        if self._api.config("light dimming") == "on":
            self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
            self._attr_color_mode = ColorMode.BRIGHTNESS
        else:
            self._attr_supported_color_modes = {ColorMode.ONOFF}
            self._attr_color_mode = ColorMode.ONOFF

    async def async_added_to_hass(self):
        """Register callbacks."""
        async_dispatcher_connect(self.hass, SIGNAL_UPDATE_SENTIO, self._update_callback)

    @callback
    def _update_callback(self):
        """Call update method."""
        _LOGGER.debug("%s update_callback state: %s", self.name, self._api.light_is_on)
        self.async_schedule_update_ha_state(True)

    @property
    def is_on(self):
        """Return the state."""
        return self._api.light_is_on

    @property
    def brightness(self):
        """Set the brightness."""
        return self._api.light_val

    async def async_turn_on(self, **kwargs):
        """Turn the light on."""
        _LOGGER.debug(
            "%s Turn_on; Brightness: %s", self.name, kwargs.get(ATTR_BRIGHTNESS)
        )
        if (brightness := kwargs.get(ATTR_BRIGHTNESS)) is not None:
            self._api.set_light_val(round(int(brightness) / 2.55))
        else:
            self._api.set_light(PYS_STATE_ON)
        self.async_schedule_update_ha_state(True)

    async def async_turn_off(self, **kwargs):
        """Turn the light off."""
        _LOGGER.debug("%s Turn_off", self.name)
        self._api.set_light(PYS_STATE_OFF)
        self.async_schedule_update_ha_state(True)

    async def async_update(self):
        """Do the update - dummy."""
        return

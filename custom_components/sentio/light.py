"""Light component for Sentio sauna controller."""

import logging

from pysentio import PYS_STATE_OFF, PYS_STATE_ON

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import SentioEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Set up the entry."""
    async_add_entities([SaunaLight(hass, entry)])


class SaunaLight(SentioEntity, LightEntity):
    """Representation of a light."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the light entity."""

        super().__init__(SentioEntity)
        self._attr_unique_id = "sauna_light"
        self._attr_translation_key = "light"
        if self._api.config("light dimming") == "on":
            self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
            self._attr_color_mode = ColorMode.BRIGHTNESS
        else:
            self._attr_supported_color_modes = {ColorMode.ONOFF}
            self._attr_color_mode = ColorMode.ONOFF

    @property
    def is_on(self) -> bool:
        """Return the state."""
        return self._api.light_is_on

    @property
    def brightness(self) -> int:
        """Set the brightness."""
        return self._api.light_val

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the light on."""
        _LOGGER.debug(
            "%s Turn_on; Brightness: %s", self.name, kwargs.get(ATTR_BRIGHTNESS)
        )
        if (brightness := kwargs.get(ATTR_BRIGHTNESS)) is not None:
            self._api.set_light_val(round(int(brightness) / 2.55))
        else:
            self._api.set_light(PYS_STATE_ON)
        self.async_schedule_update_ha_state(True)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the light off."""
        _LOGGER.debug("%s Turn_off", self.name)
        self._api.set_light(PYS_STATE_OFF)
        self.async_schedule_update_ha_state(True)

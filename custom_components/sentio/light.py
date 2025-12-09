"""Light component for Sentio sauna controller."""

import logging

from pysentio import PYS_STATE_OFF, PYS_STATE_ON

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntity,
    LightEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import SentioConfigEntry
from .entity import SentioEntity

_LOGGER = logging.getLogger(__name__)

LIGHT_DESCR = LightEntityDescription(
    key="sauna_light",
    translation_key="light",
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SentioConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the entry."""

    def get_lights() -> list[SaunaLight]:
        return [SaunaLight(hass, entry, LIGHT_DESCR)]

    async_add_entities(get_lights())


class SaunaLight(SentioEntity, LightEntity):
    """Representation of a light."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: SentioConfigEntry,
        description: LightEntityDescription,
    ) -> None:
        """Initialize the light entity."""

        super().__init__(hass, entry, description)
        if self._api.config("light dimming") == "on":
            self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
            self._attr_color_mode = ColorMode.BRIGHTNESS
        else:
            self._attr_supported_color_modes = {ColorMode.ONOFF}
            self._attr_color_mode = ColorMode.ONOFF

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

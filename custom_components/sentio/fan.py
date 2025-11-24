"""Fan entity."""

import logging
from typing import Any

from pysentio import PYS_STATE_OFF, PYS_STATE_ON

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from entity import SentioEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Set up entry."""
    async_add_entities([SaunaFan(hass, entry)])


class SaunaFan(SentioEntity, FanEntity):
    """Representation of a fan."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the fan."""
        self._attr_unique_id = "sauna_fan"
        self._attr_translation_key = "fan"

    @property
    def supported_features(self) -> FanEntityFeature:
        """Return supported features."""
        feat = FanEntityFeature.TURN_OFF | FanEntityFeature.TURN_ON
        if self._api.config("fan dimming") == "on":
            feat = feat | FanEntityFeature.SET_SPEED
        return feat

    @property
    def is_on(self) -> bool:
        """Return state."""
        return self._api.fan

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed of the fan, as a percentage."""
        _LOGGER.debug("%s Set percentage: %s", self.name, percentage)
        self._api.set_fan_val(percentage)
        self.async_schedule_update_ha_state(True)

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the fan."""
        _LOGGER.debug("%s Turn_on; percentage: %s", self.name, percentage)
        self._api.set_fan(PYS_STATE_ON)
        self.async_schedule_update_ha_state(True)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the fan."""
        _LOGGER.debug("%s Turn_off", self.name)
        self._api.set_fan(PYS_STATE_OFF)
        self.async_schedule_update_ha_state(True)

    @property
    def percentage(self) -> int | None:
        """Return percentage."""
        return self._api.fan_val

"""Fan entity."""

import logging
from typing import Any

from pysentio import PYS_STATE_OFF, PYS_STATE_ON

from homeassistant.components.fan import (
    FanEntity,
    FanEntityDescription,
    FanEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import SentioConfigEntry
from .entity import SentioEntity

_LOGGER = logging.getLogger(__name__)


FAN_DESCR = FanEntityDescription(
    key="sauna_fan",
    translation_key="fan",
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SentioConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up entry."""

    def get_fans() -> list[SaunaFan]:
        entities = []
        entities.append(SaunaFan(hass, entry, FAN_DESCR))
        return entities

    async_add_entities(get_fans())


class SaunaFan(SentioEntity, FanEntity):
    """Representation of a fan."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: SentioConfigEntry,
        description: FanEntityDescription,
    ):
        """Initialize the sensor."""

        super().__init__(hass, entry, description)

    @property
    def supported_features(self):
        """Return supported features."""
        feat = FanEntityFeature.TURN_OFF | FanEntityFeature.TURN_ON
        if self._api.config("fan dimming") == "on":
            feat = feat | FanEntityFeature.SET_SPEED
        return feat

    @property
    def is_on(self):
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

    async def async_turn_off(self, **kwargs):
        """Turn off the fan."""
        _LOGGER.debug("%s Turn_off", self.name)
        self._api.set_fan(PYS_STATE_OFF)
        self.async_schedule_update_ha_state(True)

    @property
    def percentage(self):
        """Return percentage."""
        return self._api.fan_val

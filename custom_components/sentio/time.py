"""Time component for Sentio sauna controller."""

from datetime import time
import logging

from homeassistant.components.time import TimeEntity, TimeEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import SentioEntity

_LOGGER = logging.getLogger(__name__)


delayed_start_description = TimeEntityDescription(
    key="delayed_start",
    translation_key="delayed_start_time",
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Set up the entry."""
    async_add_entities([SaunaTime(hass, entry, delayed_start_description)])


class SaunaTime(SentioEntity, TimeEntity):
    """Representation of a time."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        entity_description: TimeEntityDescription,
    ) -> None:
        """Initialize the time entity."""

        super().__init__(SentioEntity)

    @property
    def is_on(self) -> bool:
        """Return the state."""
        return self._api.light_is_on

    @property
    def native_value(self) -> time:
        """Return the time."""
        return time(12, 30)

    async def async_set_value(self, **kwargs) -> None:
        """Set the selected time."""
        return
        # self._api.set_time(time=kwargs["time"])
        # self.async_schedule_update_ha_state(True)

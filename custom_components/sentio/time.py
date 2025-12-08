"""Light component for Sentio sauna controller."""

import logging
from datetime import datetime, time

# from datetime import datetime, time, timedelta
from pysentio import SentioPro

from homeassistant.components.time import TimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
# from homeassistant.util import dt as dt_util

from .const import DOMAIN, SIGNAL_UPDATE_SENTIO

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Set up the entry."""

    def get_times() -> list[SaunaTime]:
        return [SaunaTime(hass, entry)]

    async_add_entities(get_times())


class SaunaTime(TimeEntity):
    """Representation of a light."""

    def __init__(self, hass, entry):
        """Initialize the light entity."""
        self._entryid = entry.entry_id
        self._api: SentioPro = hass.data[DOMAIN][entry.entry_id]
        self._attr_unique_id = "sauna_preset_time"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, "4321")})
        self._attr_should_poll = False
        self._attr_translation_key = "preset_time"
        self._attr_has_entity_name = True
        self.preset_time = time(14, 30)

    async def async_added_to_hass(self):
        """Register callbacks."""
        async_dispatcher_connect(self.hass, SIGNAL_UPDATE_SENTIO, self._update_callback)

    @callback
    def _update_callback(self):
        """Call update method."""
        _LOGGER.debug("%s update_callback state: %s", self.name, self._api.light_is_on)
        self.async_schedule_update_ha_state(True)

    @property
    def native_value(self) -> time:
        """Return the state."""
        return self.preset_time

    async def async_set_value(self, value: time) -> None:
        """Update the current value."""
        # now = dt_util.as_local(datetime.now())
        # interval = timedelta(
        #     hours=self.preset_time.hour(), minutes=self.preset_time.minute()
        # )
        start_time = datetime(
            0, 0, 0, minute=self.preset_time.minute(), hour=self.preset_time.hour()
        )
        minutes = int((start_time.second % (24 * 60 * 60)) / 60)
        self._api.set_timer_val(minutes)

    async def async_update(self):
        """Do the update - dummy."""
        return

"""Base entity component for Sentio sauna controller."""

import logging

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo, Entity, EntityDescription

from . import SentioConfigEntry
from .const import DOMAIN, SIGNAL_UPDATE_SENTIO, UNIQUE_IDENTIFIER

_LOGGER = logging.getLogger(__name__)


class SentioEntity(Entity):
    """Base entity class."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: SentioConfigEntry,
        entity_description: EntityDescription,
    ):
        """Initialize the base entity."""
        self.entity_description = entity_description
        self._api = entry.runtime_data.client
        self._attr_unique_id = self.entity_description.key
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, UNIQUE_IDENTIFIER)})
        self._attr_should_poll = False
        self._attr_has_entity_name = True

    async def async_added_to_hass(self):
        """Register callbacks."""
        async_dispatcher_connect(self.hass, SIGNAL_UPDATE_SENTIO, self._update_callback)

    @callback
    def _update_callback(self):
        """Call update method."""
        self.async_schedule_update_ha_state(True)

    async def async_update(self):
        """Do the update - dummy."""
        return

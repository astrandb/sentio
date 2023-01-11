"""Switch module for Sentio integration."""
import logging

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect, dispatcher_send
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from pysentio import PYS_STATE_OFF, PYS_STATE_ON

from .const import DOMAIN, SIGNAL_UPDATE_SENTIO

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup the switches."""

    def get_entities():
        entities = [SaunaOn(hass, entry)]
        entities.append(TimerSwitch(hass, entry, timer_desc))
        return entities

    async_add_entities(await hass.async_add_job(get_entities), True)


class SaunaOn(SwitchEntity):
    """Representation of a switch."""

    def __init__(self, hass, entry):
        """Initialize the sensor."""
        self._entryid = entry.entry_id
        self._attr_unique_id = "sauna_switch"
        self._attr_has_entity_name = True
        self._attr_should_poll = False
        self._attr_name = "Heater"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, "4321")})
        self._attr_icon = "mdi:radiator"
        self._api = hass.data[DOMAIN][entry.entry_id]

    async def async_added_to_hass(self):
        """Register callbacks."""
        async_dispatcher_connect(self.hass, SIGNAL_UPDATE_SENTIO, self._update_callback)

    @callback
    def _update_callback(self):
        """Call update method."""
        _LOGGER.debug("%s update_callback state: %s", self.name, self._api.is_on)
        self.async_schedule_update_ha_state(True)

    @property
    def is_on(self):
        return self._api.is_on

    async def async_turn_on(self, **kwargs):
        _LOGGER.debug("%s Turn_on", self.name)
        self._api.set_sauna(PYS_STATE_ON)
        self.async_schedule_update_ha_state(True)
        dispatcher_send(self.hass, SIGNAL_UPDATE_SENTIO)

    async def async_turn_off(self, **kwargs):
        _LOGGER.debug("%s Turn_off", self.name)
        self._api.set_sauna(PYS_STATE_OFF)
        self.async_schedule_update_ha_state(True)
        dispatcher_send(self.hass, SIGNAL_UPDATE_SENTIO)

    async def async_update(self):
        """Update."""
        _LOGGER.debug("%s Switch async_update 1 %s", self.name, self._api.is_on)


timer_desc = SwitchEntityDescription(
    key="preset_timer",
    entity_category=EntityCategory.DIAGNOSTIC,
    has_entity_name=True,
    icon="mdi:progress-clock",
    name="Preset timer",
)


class TimerSwitch(SwitchEntity):
    """Representation of a timer switch."""

    entity_description: SwitchEntityDescription

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        description: SwitchEntityDescription,
    ):
        self.entity_description = description
        self._api = hass.data[DOMAIN][entry.entry_id]
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, "4321")})
        self._attr_unique_id = self.entity_description.key

    @property
    def is_on(self):
        if self.entity_description.key == "preset_timer":
            return self._api.timer_is_on
        if self.entity_description.key == "heater_timer":
            return self._api.heattimer_is_on
        return None

    async def async_turn_on(self, **kwargs):
        if self.entity_description.key == "preset_timer":
            self._api.set_timer(PYS_STATE_ON)
        if self.entity_description.key == "heater_timer":
            self._api.set_heattimer(PYS_STATE_ON)
        self.async_schedule_update_ha_state(True)
        dispatcher_send(self.hass, SIGNAL_UPDATE_SENTIO)

    async def async_turn_off(self, **kwargs):
        if self.entity_description.key == "preset_timer":
            self._api.set_timer(PYS_STATE_OFF)
        if self.entity_description.key == "heater_timer":
            self._api.set_heattimer(PYS_STATE_OFF)
        self.async_schedule_update_ha_state(True)
        dispatcher_send(self.hass, SIGNAL_UPDATE_SENTIO)

    async def async_added_to_hass(self):
        """Register callbacks."""
        async_dispatcher_connect(self.hass, SIGNAL_UPDATE_SENTIO, self._update_callback)

    @callback
    def _update_callback(self):
        """Call update method."""
        self.async_schedule_update_ha_state(True)

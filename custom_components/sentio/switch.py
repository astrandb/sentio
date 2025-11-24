"""Switch module for Sentio integration."""

import logging

from pysentio import PYS_STATE_OFF, PYS_STATE_ON

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import SIGNAL_UPDATE_SENTIO
from .entity import SentioEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Set up the switches."""

    def get_entities() -> list[SwitchEntity]:
        entities = [SaunaOn(hass, entry)]
        entities.append(TimerSwitch(hass, entry, timer_desc))
        return entities

    async_add_entities(get_entities())


class SaunaOn(SentioEntity, SwitchEntity):
    """Representation of a switch."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize the sensor."""
        super().__init__(SentioEntity)
        self._attr_unique_id = "sauna_switch"
        self._attr_translation_key = "heater"
        self._attr_icon = "mdi:radiator"

    @property
    def is_on(self) -> None:
        """Return state."""
        return self._api.is_on

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on the switch."""
        _LOGGER.debug("%s Turn_on", self.name)
        self._api.set_sauna(PYS_STATE_ON)
        self.async_schedule_update_ha_state(True)
        dispatcher_send(self.hass, SIGNAL_UPDATE_SENTIO)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the switch."""
        _LOGGER.debug("%s Turn_off", self.name)
        self._api.set_sauna(PYS_STATE_OFF)
        self.async_schedule_update_ha_state(True)
        dispatcher_send(self.hass, SIGNAL_UPDATE_SENTIO)


timer_desc = SwitchEntityDescription(
    key="preset_timer",
    entity_category=EntityCategory.DIAGNOSTIC,
    icon="mdi:progress-clock",
    translation_key="preset_timer",
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
        """Init the TimerSwitch class."""
        self.entity_description = description

    @property
    def is_on(self) -> None:
        """Return the state."""
        if self.entity_description.key == "preset_timer":
            return self._api.timer_is_on
        if self.entity_description.key == "heater_timer":
            return self._api.heattimer_is_on
        return None

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on the preset timer."""
        if self.entity_description.key == "preset_timer":
            self._api.set_timer(PYS_STATE_ON)
        if self.entity_description.key == "heater_timer":
            self._api.set_heattimer(PYS_STATE_ON)
        self.async_schedule_update_ha_state(True)
        dispatcher_send(self.hass, SIGNAL_UPDATE_SENTIO)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the preset timer."""
        if self.entity_description.key == "preset_timer":
            self._api.set_timer(PYS_STATE_OFF)
        if self.entity_description.key == "heater_timer":
            self._api.set_heattimer(PYS_STATE_OFF)
        self.async_schedule_update_ha_state(True)
        dispatcher_send(self.hass, SIGNAL_UPDATE_SENTIO)

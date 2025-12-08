"""Test initial setup."""

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.sentio import async_unload_entry
from custom_components.sentio.const import DOMAIN
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant

from . import setup_integration
from .const import ENTRY_ID, MOCK_CONFIG


async def test_setup_entry(hass: HomeAssistant, mock_sentio_client) -> None:
    """Test setup entry."""
    entry = MockConfigEntry(
        domain=DOMAIN, version=3, data=MOCK_CONFIG, entry_id=ENTRY_ID
    )
    await setup_integration(hass, entry)

    assert entry.state is ConfigEntryState.LOADED

    assert await async_unload_entry(hass, entry)
    assert DOMAIN not in hass.data

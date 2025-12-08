"""pytest fixtures."""

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import load_fixture
from pytest_homeassistant_custom_component.syrupy import HomeAssistantSnapshotExtension
from syrupy import SnapshotAssertion

from homeassistant.util.json import json_loads

# pylint: disable=redefined-outer-name


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations defined in the test dir."""
    return


@pytest.fixture
def data_file_name() -> str:
    """Filename for data fixture."""
    return "sentio_pro_d2.json"


@pytest.fixture(name="load_default_sauna")
def load_default_sauna_fixture(data_file_name: str) -> dict:
    """Load data for default sauna."""
    return json_loads(load_fixture(data_file_name))


@pytest.fixture
def snapshot(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    """Return snapshot assertion fixture with the Home Assistant extension."""
    return snapshot.use_extension(HomeAssistantSnapshotExtension)


@pytest.fixture
def mock_sentio_client() -> Generator[MagicMock]:
    """Skip calls to get data from API."""
    with patch(
        "custom_components.sentio.SentioPro",
        autospec=True,
    ) as mock_client:
        client = mock_client.return_value
        client.is_on.return_value = False
        client.sauna_val.return_value = 28
        client.target_temperature.return_value = 75
        client.light_is_on.return_value = False
        client.light_val.return_value = 50
        client.fan.return_value = False
        client.fan_val.return_value = 60
        client.steam.return_value = False
        client.steam_val.return_value = 70
        client.i_switch.return_value = False
        client.i_switch_val.return_value = 40
        client.heattimer_is_on.return_value = False
        client.heattimer_val.return_value = 300
        client.timer_is_on.return_value = False
        client.timer_val.return_value = 60
        client.heater_temperature.return_value = 30
        client.bench_temperature.return_value = 40
        client.foil_temperature.return_value = 50
        client.humidity.return_value = 90
        client.user_prog_is_on.return_value = False
        client.user_prog_val.return_value = 1
        client.hvac_mode.return_value = "off"
        client.sw_version.return_value = "TheVersion"
        client.type.return_value = "Type X"
        client.config.return_value = None
        client.config_raw.return_value = "abc"
        client.status.return_value = "OK"

        yield client


@pytest.fixture
def entity_registry_enabled_by_default() -> Generator[None]:
    """Test fixture that ensures all entities are enabled in the registry."""
    with patch(
        "homeassistant.helpers.entity.Entity.entity_registry_enabled_default",
        return_value=True,
    ):
        yield

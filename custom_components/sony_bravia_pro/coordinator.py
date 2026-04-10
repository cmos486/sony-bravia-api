"""DataUpdateCoordinator for Sony Bravia Pro."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .bravia_client import (
    BraviaClient,
    BraviaConnectionError,
    BraviaError,
    BraviaTurnedOffError,
)
from .const import (
    CONF_PSK,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    POWER_STATUS_ACTIVE,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class BraviaState:
    """Representation of the TV's current state."""

    power: str = "standby"
    volume: int | None = None
    is_muted: bool | None = None
    max_volume: int = 100
    min_volume: int = 0
    playing_content: dict[str, Any] = field(default_factory=dict)
    external_inputs: list[dict[str, Any]] = field(default_factory=list)
    app_list: list[dict[str, Any]] = field(default_factory=list)
    app_status: list[dict[str, str]] = field(default_factory=list)
    is_available: bool = False

    @property
    def is_on(self) -> bool:
        """Return True if the TV is on."""
        return self.power == POWER_STATUS_ACTIVE


class BraviaCoordinator(DataUpdateCoordinator[BraviaState]):
    """Coordinator to poll Sony Bravia Pro TV state."""

    config_entry: ConfigEntry
    client: BraviaClient
    ircc_codes: dict[str, str]
    system_info: dict[str, Any]
    _app_list_fetched: bool

    def __init__(
        self,
        hass: HomeAssistant,
        client: BraviaClient,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.data[CONF_HOST]}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
            config_entry=entry,
        )
        self.client = client
        self.ircc_codes = {}
        self.system_info = {}
        self._app_list_fetched = False

    async def async_setup(self) -> None:
        """Perform one-time setup: fetch system info and IRCC codes."""
        try:
            self.system_info = await self.client.get_system_info()
        except BraviaError as err:
            _LOGGER.warning("Could not fetch system info: %s", err)
            self.system_info = dict(self.config_entry.data)

        try:
            codes = await self.client.get_remote_controller_info()
            self.ircc_codes = {
                item["name"]: item["value"]
                for item in codes
                if isinstance(item, dict) and "name" in item and "value" in item
            }
            _LOGGER.debug(
                "Loaded %d IRCC codes from %s",
                len(self.ircc_codes),
                self.client.host,
            )
        except BraviaError as err:
            _LOGGER.warning("Could not fetch IRCC codes: %s", err)

    async def _async_update_data(self) -> BraviaState:
        """Fetch latest state from the TV."""
        state = BraviaState()

        # Always try to get power status first
        try:
            state.power = await self.client.get_power_status()
            state.is_available = True
        except BraviaConnectionError:
            state.is_available = False
            state.power = "standby"
            return state
        except BraviaError as err:
            raise UpdateFailed(f"Error fetching power status: {err}") from err

        # If TV is off, return minimal state
        if not state.is_on:
            return state

        # TV is on — fetch detailed state
        try:
            volume_info = await self.client.get_volume_info()
            for item in volume_info:
                if isinstance(item, dict) and item.get("target") in (
                    "speaker",
                    "",
                ):
                    state.volume = item.get("volume")
                    state.is_muted = item.get("mute", False)
                    state.max_volume = item.get("maxVolume", 100)
                    state.min_volume = item.get("minVolume", 0)
                    break
        except BraviaError as err:
            _LOGGER.debug("Could not fetch volume info: %s", err)

        try:
            state.playing_content = await self.client.get_playing_content()
        except (BraviaTurnedOffError, BraviaError) as err:
            _LOGGER.debug("Could not fetch playing content: %s", err)

        try:
            state.external_inputs = await self.client.get_external_inputs()
        except BraviaError as err:
            _LOGGER.debug("Could not fetch external inputs: %s", err)

        # Fetch app list once (it rarely changes)
        if not self._app_list_fetched:
            try:
                state.app_list = await self.client.get_app_list()
                self._app_list_fetched = True
            except BraviaError as err:
                _LOGGER.debug("Could not fetch app list: %s", err)
        else:
            # Reuse previous app list
            if self.data and self.data.app_list:
                state.app_list = self.data.app_list

        try:
            state.app_status = await self.client.get_app_status_list()
        except BraviaError as err:
            _LOGGER.debug("Could not fetch app status: %s", err)

        return state

    def get_ircc_code(self, command: str) -> str | None:
        """Look up an IRCC code by command name."""
        return self.ircc_codes.get(command)

    async def send_ircc_by_name(self, command: str) -> None:
        """Send an IRCC code by command name."""
        code = self.get_ircc_code(command)
        if code is None:
            _LOGGER.error(
                "Unknown IRCC command '%s'. Available: %s",
                command,
                ", ".join(sorted(self.ircc_codes.keys())),
            )
            return
        await self.client.send_ircc(code)

    async def refresh_app_list(self) -> None:
        """Force a refresh of the application list."""
        self._app_list_fetched = False
        await self.async_request_refresh()

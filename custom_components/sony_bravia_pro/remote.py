"""Remote entity for Sony Bravia Pro (IRCC commands)."""

from __future__ import annotations

from collections.abc import Iterable
import logging
from typing import Any

from homeassistant.components.remote import RemoteEntity, RemoteEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .bravia_client import BraviaError
from .const import DOMAIN
from .coordinator import BraviaCoordinator
from .entity import BraviaEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Sony Bravia Pro remote."""
    coordinator: BraviaCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([BraviaRemote(coordinator, entry)])


class BraviaRemote(BraviaEntity, RemoteEntity):
    """Sony Bravia Pro remote control entity."""

    _attr_translation_key = "remote"
    _attr_name = "Remote"
    _attr_supported_features = RemoteEntityFeature(0)

    def __init__(
        self,
        coordinator: BraviaCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.unique_id}_remote"

    @property
    def is_on(self) -> bool:
        """Return True if the TV is on."""
        data = self.coordinator.data
        return data.is_on if data else False

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return available IRCC commands as an attribute."""
        return {
            "available_commands": sorted(self.coordinator.ircc_codes.keys())
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the TV on."""
        try:
            await self.coordinator.client.power_on()
        except BraviaError as err:
            _LOGGER.error("Failed to turn on: %s", err)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the TV off."""
        try:
            await self.coordinator.client.power_off()
        except BraviaError as err:
            _LOGGER.error("Failed to turn off: %s", err)
        await self.coordinator.async_request_refresh()

    async def async_send_command(
        self,
        command: Iterable[str],
        **kwargs: Any,
    ) -> None:
        """Send IRCC commands to the TV.

        Accepts both command names (e.g., 'VolumeUp') and raw IRCC codes
        (base64 strings ending in '==').
        """
        num_repeats = kwargs.get("num_repeats", 1)
        delay_secs = kwargs.get("delay_secs", 0.0)

        for _ in range(num_repeats):
            for cmd in command:
                try:
                    if cmd.endswith("==") or cmd.endswith("Aw=="):
                        # Looks like a raw IRCC code
                        await self.coordinator.client.send_ircc(cmd)
                    else:
                        # Look up by name
                        await self.coordinator.send_ircc_by_name(cmd)
                except BraviaError as err:
                    _LOGGER.error("Failed to send IRCC command '%s': %s", cmd, err)

            if delay_secs > 0 and num_repeats > 1:
                import asyncio
                await asyncio.sleep(delay_secs)

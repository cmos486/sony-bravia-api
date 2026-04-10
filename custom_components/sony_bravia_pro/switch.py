"""Switch entities for Sony Bravia Pro."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
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
    """Set up Sony Bravia Pro switches."""
    coordinator: BraviaCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            BraviaLEDSwitch(coordinator, entry),
            BraviaWoLSwitch(coordinator, entry),
        ]
    )


class BraviaLEDSwitch(BraviaEntity, SwitchEntity):
    """Switch to control the LED indicator."""

    _attr_translation_key = "led_indicator"
    _attr_icon = "mdi:led-on"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: BraviaCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.unique_id}_led_indicator"
        self._is_on: bool | None = None

    @property
    def is_on(self) -> bool | None:
        """Return True if LED is on."""
        return self._is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the LED."""
        try:
            await self.coordinator.client.set_led_status(True)
            self._is_on = True
        except BraviaError as err:
            _LOGGER.error("Failed to turn on LED: %s", err)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the LED."""
        try:
            await self.coordinator.client.set_led_status(False)
            self._is_on = False
        except BraviaError as err:
            _LOGGER.error("Failed to turn off LED: %s", err)

    async def async_added_to_hass(self) -> None:
        """Fetch initial LED state."""
        await super().async_added_to_hass()
        try:
            self._is_on = await self.coordinator.client.get_led_status()
        except BraviaError:
            pass


class BraviaWoLSwitch(BraviaEntity, SwitchEntity):
    """Switch to control Wake-on-LAN mode."""

    _attr_translation_key = "wake_on_lan"
    _attr_icon = "mdi:power-plug"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        coordinator: BraviaCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.unique_id}_wake_on_lan"
        self._is_on: bool | None = None

    @property
    def is_on(self) -> bool | None:
        """Return True if WoL is enabled."""
        return self._is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable WoL."""
        try:
            await self.coordinator.client.set_wol_mode(True)
            self._is_on = True
        except BraviaError as err:
            _LOGGER.error("Failed to enable WoL: %s", err)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable WoL."""
        try:
            await self.coordinator.client.set_wol_mode(False)
            self._is_on = False
        except BraviaError as err:
            _LOGGER.error("Failed to disable WoL: %s", err)

    async def async_added_to_hass(self) -> None:
        """Fetch initial WoL state."""
        await super().async_added_to_hass()
        try:
            self._is_on = await self.coordinator.client.get_wol_mode()
        except BraviaError:
            pass

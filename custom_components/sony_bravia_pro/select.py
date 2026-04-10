"""Select entities for Sony Bravia Pro."""

from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .bravia_client import BraviaError
from .const import (
    DOMAIN,
    SCREEN_ROTATION_OPTIONS,
    SOUND_OUTPUT_OPTIONS,
)
from .coordinator import BraviaCoordinator
from .entity import BraviaEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sony Bravia Pro select entities."""
    coordinator: BraviaCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            BraviaSoundOutputSelect(coordinator, entry),
            BraviaScreenRotationSelect(coordinator, entry),
        ]
    )


class BraviaSoundOutputSelect(BraviaEntity, SelectEntity):
    """Select entity for sound output mode."""

    _attr_translation_key = "sound_output"
    _attr_icon = "mdi:speaker"

    def __init__(
        self,
        coordinator: BraviaCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.unique_id}_sound_output"
        self._attr_options = list(SOUND_OUTPUT_OPTIONS.values())
        self._current: str | None = None

    @property
    def current_option(self) -> str | None:
        """Return current sound output."""
        return self._current

    async def async_select_option(self, option: str) -> None:
        """Set the sound output mode."""
        # Reverse lookup: display name -> API value
        api_value = None
        for key, label in SOUND_OUTPUT_OPTIONS.items():
            if label == option:
                api_value = key
                break

        if api_value is None:
            _LOGGER.error("Unknown sound output option: %s", option)
            return

        try:
            await self.coordinator.client.set_sound_settings(
                [{"target": "outputTerminal", "value": api_value}]
            )
            self._current = option
        except BraviaError as err:
            _LOGGER.error("Failed to set sound output: %s", err)

    async def async_added_to_hass(self) -> None:
        """Fetch initial sound output setting when added."""
        await super().async_added_to_hass()
        try:
            settings = await self.coordinator.client.get_speaker_settings(
                "outputTerminal"
            )
            if settings:
                for setting in settings:
                    if isinstance(setting, dict) and setting.get("target") == "outputTerminal":
                        value = setting.get("currentValue", "")
                        self._current = SOUND_OUTPUT_OPTIONS.get(value)
                        break
        except BraviaError:
            pass


class BraviaScreenRotationSelect(BraviaEntity, SelectEntity):
    """Select entity for screen rotation."""

    _attr_translation_key = "screen_rotation"
    _attr_icon = "mdi:screen-rotation"

    def __init__(
        self,
        coordinator: BraviaCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.unique_id}_screen_rotation"
        self._attr_options = list(SCREEN_ROTATION_OPTIONS.values())
        self._current_angle: int = 0

    @property
    def current_option(self) -> str | None:
        """Return current rotation."""
        return SCREEN_ROTATION_OPTIONS.get(self._current_angle)

    async def async_select_option(self, option: str) -> None:
        """Set screen rotation."""
        # Reverse lookup: display name -> angle
        angle = None
        for a, label in SCREEN_ROTATION_OPTIONS.items():
            if label == option:
                angle = a
                break

        if angle is None:
            _LOGGER.error("Unknown rotation option: %s", option)
            return

        try:
            await self.coordinator.client.set_screen_rotation(angle)
            self._current_angle = angle
        except BraviaError as err:
            _LOGGER.error("Failed to set screen rotation: %s", err)

    async def async_added_to_hass(self) -> None:
        """Fetch initial rotation when added."""
        await super().async_added_to_hass()
        try:
            self._current_angle = await self.coordinator.client.get_screen_rotation()
        except BraviaError:
            pass

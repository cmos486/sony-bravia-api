"""Button entities for Sony Bravia Pro."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .bravia_client import BraviaClient, BraviaError
from .const import DOMAIN, POWER_SAVING_OFF, POWER_SAVING_PICTURE_OFF
from .coordinator import BraviaCoordinator
from .entity import BraviaEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class BraviaButtonDescription(ButtonEntityDescription):
    """Describe a Bravia button entity."""

    press_fn: Callable[[BraviaClient], Coroutine[Any, Any, None]]


BUTTON_DESCRIPTIONS: tuple[BraviaButtonDescription, ...] = (
    BraviaButtonDescription(
        key="reboot",
        translation_key="reboot",
        icon="mdi:restart",
        press_fn=lambda client: client.request_reboot(),
    ),
    BraviaButtonDescription(
        key="terminate_apps",
        translation_key="terminate_apps",
        icon="mdi:close-box-multiple",
        press_fn=lambda client: client.terminate_apps(),
    ),
    BraviaButtonDescription(
        key="picture_off",
        translation_key="picture_off",
        icon="mdi:monitor-off",
        press_fn=lambda client: client.set_power_saving_mode(
            POWER_SAVING_PICTURE_OFF
        ),
    ),
    BraviaButtonDescription(
        key="picture_on",
        translation_key="picture_on",
        icon="mdi:monitor",
        press_fn=lambda client: client.set_power_saving_mode(POWER_SAVING_OFF),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sony Bravia Pro buttons."""
    coordinator: BraviaCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        BraviaButton(coordinator, entry, desc) for desc in BUTTON_DESCRIPTIONS
    )


class BraviaButton(BraviaEntity, ButtonEntity):
    """A Sony Bravia Pro button entity."""

    entity_description: BraviaButtonDescription

    def __init__(
        self,
        coordinator: BraviaCoordinator,
        entry: ConfigEntry,
        description: BraviaButtonDescription,
    ) -> None:
        super().__init__(coordinator, entry)
        self.entity_description = description
        self._attr_unique_id = f"{entry.unique_id}_{description.key}"

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            await self.entity_description.press_fn(self.coordinator.client)
        except BraviaError as err:
            _LOGGER.error(
                "Failed to execute %s: %s",
                self.entity_description.key,
                err,
            )

"""Sensor entities for Sony Bravia Pro."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import BraviaCoordinator
from .entity import BraviaEntity


@dataclass(frozen=True, kw_only=True)
class BraviaSensorDescription(SensorEntityDescription):
    """Describe a Bravia sensor entity."""

    value_fn: Callable[[dict[str, Any]], str | None]


SENSOR_DESCRIPTIONS: tuple[BraviaSensorDescription, ...] = (
    BraviaSensorDescription(
        key="model",
        translation_key="model",
        icon="mdi:television",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda info: info.get("model"),
    ),
    BraviaSensorDescription(
        key="firmware",
        translation_key="firmware",
        icon="mdi:chip",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda info: info.get("generation"),
    ),
    BraviaSensorDescription(
        key="serial_number",
        translation_key="serial_number",
        icon="mdi:identifier",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda info: info.get("serial"),
    ),
    BraviaSensorDescription(
        key="mac_address",
        translation_key="mac_address",
        icon="mdi:ethernet",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda info: info.get("macAddr"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sony Bravia Pro sensors."""
    coordinator: BraviaCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        BraviaSensor(coordinator, entry, desc) for desc in SENSOR_DESCRIPTIONS
    )


class BraviaSensor(BraviaEntity, SensorEntity):
    """A Sony Bravia Pro diagnostic sensor."""

    entity_description: BraviaSensorDescription

    def __init__(
        self,
        coordinator: BraviaCoordinator,
        entry: ConfigEntry,
        description: BraviaSensorDescription,
    ) -> None:
        super().__init__(coordinator, entry)
        self.entity_description = description
        self._attr_unique_id = f"{entry.unique_id}_{description.key}"

    @property
    def native_value(self) -> str | None:
        """Return the sensor value from system info."""
        return self.entity_description.value_fn(self.coordinator.system_info)

    @property
    def available(self) -> bool:
        """Diagnostic sensors are always available if coordinator is running."""
        return True

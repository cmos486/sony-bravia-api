"""Base entity for Sony Bravia Pro integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BraviaCoordinator, BraviaState


class BraviaEntity(CoordinatorEntity[BraviaCoordinator]):
    """Base class for Sony Bravia Pro entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: BraviaCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        info = coordinator.system_info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id or entry.entry_id)},
            name=info.get("model") or info.get("name") or "Sony Bravia Pro",
            manufacturer="Sony",
            model=info.get("model"),
            sw_version=info.get("generation") or info.get("firmware"),
            serial_number=info.get("serial"),
        )

    @property
    def available(self) -> bool:
        """Return True if the TV is reachable."""
        return super().available and self.coordinator.data.is_available

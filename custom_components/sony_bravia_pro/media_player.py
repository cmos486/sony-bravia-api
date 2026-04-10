"""Media player entity for Sony Bravia Pro."""

from __future__ import annotations

import asyncio
import logging
import socket
from typing import Any

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .bravia_client import BraviaError
from .const import CONF_MAC, DOMAIN, WOL_PORT
from .coordinator import BraviaCoordinator
from .entity import BraviaEntity

_LOGGER = logging.getLogger(__name__)

# BrowseMedia may not be available in all HA versions
try:
    from homeassistant.components.media_player import BrowseMedia

    _HAS_BROWSE_MEDIA = True
except ImportError:
    _HAS_BROWSE_MEDIA = False

SOURCE_TYPE_INPUT = "input"
SOURCE_TYPE_APP = "app"

_BASE_FEATURES = (
    MediaPlayerEntityFeature.TURN_ON
    | MediaPlayerEntityFeature.TURN_OFF
    | MediaPlayerEntityFeature.VOLUME_SET
    | MediaPlayerEntityFeature.VOLUME_STEP
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.SELECT_SOURCE
    | MediaPlayerEntityFeature.PLAY_MEDIA
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Sony Bravia Pro media player."""
    coordinator: BraviaCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([BraviaMediaPlayer(coordinator, entry)])


class BraviaMediaPlayer(BraviaEntity, MediaPlayerEntity):
    """Representation of a Sony Bravia Pro TV as a media player."""

    _attr_device_class = MediaPlayerDeviceClass.TV
    _attr_name = None  # Use device name

    def __init__(
        self,
        coordinator: BraviaCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.unique_id}_media_player"
        self._sources: dict[str, dict[str, str]] = {}
        self._mac = entry.data.get(CONF_MAC)

        features = _BASE_FEATURES
        if _HAS_BROWSE_MEDIA:
            features |= MediaPlayerEntityFeature.BROWSE_MEDIA
        self._attr_supported_features = features

    def _build_source_map(self) -> None:
        """Build source map from external inputs and apps."""
        self._sources = {}
        data = self.coordinator.data
        if not data:
            return

        for inp in data.external_inputs:
            label = inp.get("title", "")
            custom_label = inp.get("label", "")
            uri = inp.get("uri", "")
            name = custom_label if custom_label else label
            if name and uri:
                self._sources[name] = {"uri": uri, "type": SOURCE_TYPE_INPUT}

        for app in data.app_list:
            title = app.get("title", "")
            uri = app.get("uri", "")
            if title and uri:
                self._sources[title] = {"uri": uri, "type": SOURCE_TYPE_APP}

    @property
    def state(self) -> MediaPlayerState | None:
        """Return the current state."""
        data = self.coordinator.data
        if not data or not data.is_available:
            return MediaPlayerState.OFF
        if not data.is_on:
            return MediaPlayerState.OFF
        if data.playing_content and data.playing_content.get("uri"):
            return MediaPlayerState.ON
        return MediaPlayerState.IDLE

    @property
    def volume_level(self) -> float | None:
        """Return the volume level (0..1)."""
        data = self.coordinator.data
        if not data or data.volume is None or data.max_volume == 0:
            return None
        return data.volume / data.max_volume

    @property
    def is_volume_muted(self) -> bool | None:
        """Return True if volume is muted."""
        data = self.coordinator.data
        return data.is_muted if data else None

    @property
    def source(self) -> str | None:
        """Return the current source."""
        data = self.coordinator.data
        if not data or not data.playing_content:
            return None
        uri = data.playing_content.get("uri", "")
        title = data.playing_content.get("title", "")

        self._build_source_map()
        for name, src in self._sources.items():
            if src["uri"] == uri:
                return name

        return title or uri or None

    @property
    def source_list(self) -> list[str]:
        """Return the list of available sources."""
        self._build_source_map()
        return list(self._sources.keys())

    @property
    def media_title(self) -> str | None:
        """Return the title of current content."""
        data = self.coordinator.data
        if data and data.playing_content:
            return data.playing_content.get("title")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes including installed apps."""
        attrs: dict[str, Any] = {}
        data = self.coordinator.data
        if data and data.app_list:
            attrs["installed_apps"] = {
                app.get("title", "Unknown"): app.get("uri", "")
                for app in data.app_list
                if app.get("title") and app.get("uri")
            }
        return attrs

    async def async_turn_on(self) -> None:
        """Turn the TV on."""
        if self._mac:
            await self._send_wol()
        try:
            await self.coordinator.client.power_on()
        except BraviaError:
            _LOGGER.debug("Could not power on via API, WoL sent if MAC available")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn the TV off."""
        try:
            await self.coordinator.client.power_off()
        except BraviaError as err:
            _LOGGER.error("Failed to turn off: %s", err)
        await self.coordinator.async_request_refresh()

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level (0..1)."""
        data = self.coordinator.data
        max_vol = data.max_volume if data else 100
        target = round(volume * max_vol)
        try:
            await self.coordinator.client.set_volume(str(target))
        except BraviaError as err:
            _LOGGER.error("Failed to set volume: %s", err)
        await self.coordinator.async_request_refresh()

    async def async_volume_up(self) -> None:
        """Volume up."""
        try:
            await self.coordinator.client.volume_up()
        except BraviaError as err:
            _LOGGER.error("Failed to volume up: %s", err)
        await self.coordinator.async_request_refresh()

    async def async_volume_down(self) -> None:
        """Volume down."""
        try:
            await self.coordinator.client.volume_down()
        except BraviaError as err:
            _LOGGER.error("Failed to volume down: %s", err)
        await self.coordinator.async_request_refresh()

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute/unmute the volume."""
        try:
            await self.coordinator.client.set_mute(mute)
        except BraviaError as err:
            _LOGGER.error("Failed to set mute: %s", err)
        await self.coordinator.async_request_refresh()

    async def async_select_source(self, source: str) -> None:
        """Select input source."""
        self._build_source_map()
        src = self._sources.get(source)
        if src is None:
            _LOGGER.error("Unknown source: %s", source)
            return

        try:
            if src["type"] == SOURCE_TYPE_APP:
                await self.coordinator.client.set_active_app(src["uri"])
            else:
                await self.coordinator.client.set_play_content(src["uri"])
        except BraviaError as err:
            _LOGGER.error("Failed to select source %s: %s", source, err)
        await self.coordinator.async_request_refresh()

    async def async_play_media(
        self, media_type: str, media_id: str, **kwargs: Any
    ) -> None:
        """Play media (launch app or switch input by URI)."""
        try:
            if media_type == "app":
                await self.coordinator.client.set_active_app(media_id)
            else:
                await self.coordinator.client.set_play_content(media_id)
        except BraviaError as err:
            _LOGGER.error("Failed to play media %s: %s", media_id, err)
        await self.coordinator.async_request_refresh()

    async def async_browse_media(
        self,
        media_content_type: str | None = None,
        media_content_id: str | None = None,
    ) -> Any:
        """Implement media browsing: list apps and inputs."""
        if not _HAS_BROWSE_MEDIA:
            raise NotImplementedError("BrowseMedia not available in this HA version")

        if media_content_type is None or media_content_id is None:
            return BrowseMedia(
                media_class="directory",
                media_content_id="root",
                media_content_type="directory",
                title="Sony Bravia Pro",
                can_play=False,
                can_expand=True,
                children=[
                    BrowseMedia(
                        media_class="directory",
                        media_content_id="inputs",
                        media_content_type="directory",
                        title="Inputs",
                        can_play=False,
                        can_expand=True,
                    ),
                    BrowseMedia(
                        media_class="directory",
                        media_content_id="apps",
                        media_content_type="directory",
                        title="Applications",
                        can_play=False,
                        can_expand=True,
                    ),
                ],
            )

        children = []
        data = self.coordinator.data

        if media_content_id == "inputs" and data:
            for inp in data.external_inputs:
                label = inp.get("label") or inp.get("title", "Unknown")
                uri = inp.get("uri", "")
                children.append(
                    BrowseMedia(
                        media_class="channel",
                        media_content_id=uri,
                        media_content_type="input",
                        title=label,
                        can_play=True,
                        can_expand=False,
                    )
                )
        elif media_content_id == "apps" and data:
            for app in data.app_list:
                title = app.get("title", "Unknown")
                uri = app.get("uri", "")
                icon = app.get("icon", "")
                children.append(
                    BrowseMedia(
                        media_class="app",
                        media_content_id=uri,
                        media_content_type="app",
                        title=title,
                        can_play=True,
                        can_expand=False,
                        thumbnail=icon or None,
                    )
                )

        return BrowseMedia(
            media_class="directory",
            media_content_id=media_content_id,
            media_content_type="directory",
            title="Inputs" if media_content_id == "inputs" else "Applications",
            can_play=False,
            can_expand=True,
            children=children,
        )

    async def _send_wol(self) -> None:
        """Send a Wake-on-LAN magic packet."""
        if not self._mac:
            return
        try:
            mac_bytes = bytes.fromhex(self._mac.replace(":", "").replace("-", ""))
        except ValueError:
            _LOGGER.error("Invalid MAC address for WoL: %s", self._mac)
            return

        magic = b"\xff" * 6 + mac_bytes * 16

        loop = asyncio.get_running_loop()
        transport, _ = await loop.create_datagram_endpoint(
            asyncio.DatagramProtocol,
            family=socket.AF_INET,
        )
        try:
            transport.sendto(magic, ("255.255.255.255", WOL_PORT))
        finally:
            transport.close()

        _LOGGER.debug("Sent WoL magic packet to %s", self._mac)

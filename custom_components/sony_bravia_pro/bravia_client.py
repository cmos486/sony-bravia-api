"""Sony Bravia Pro REST API client."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

from .const import (
    DEFAULT_PORT,
    IRCC_SOAP_ACTION,
    IRCC_SOAP_BODY,
    REQUEST_TIMEOUT,
    SERVICE_APP_CONTROL,
    SERVICE_AUDIO,
    SERVICE_AV_CONTENT,
    SERVICE_GUIDE,
    SERVICE_SYSTEM,
    SERVICE_VIDEO,
    SERVICE_VIDEO_SCREEN,
)

_LOGGER = logging.getLogger(__name__)


class BraviaError(Exception):
    """Base exception for Bravia API errors."""


class BraviaConnectionError(BraviaError):
    """TV is unreachable (off/suspend/network error)."""


class BraviaAuthError(BraviaError):
    """Invalid or missing PSK."""


class BraviaTurnedOffError(BraviaError):
    """TV is powered off and cannot process the request (API error code 7)."""


class BraviaApiError(BraviaError):
    """Generic API error with code and message."""

    def __init__(self, code: int, message: str) -> None:
        super().__init__(f"Bravia API error {code}: {message}")
        self.code = code
        self.message = message


class BraviaClient:
    """Async client for Sony Bravia Pro REST API."""

    def __init__(
        self,
        host: str,
        psk: str,
        session: aiohttp.ClientSession,
        port: int = DEFAULT_PORT,
    ) -> None:
        self._host = host
        self._psk = psk
        self._session = session
        self._port = port
        self._base_url = f"http://{host}:{port}/sony"
        self._request_id = 0

    @property
    def host(self) -> str:
        """Return the host address."""
        return self._host

    # ------------------------------------------------------------------
    # Core request methods
    # ------------------------------------------------------------------

    async def _request(
        self,
        service: str,
        method: str,
        params: list[Any] | None = None,
        version: str = "1.0",
    ) -> Any:
        """Send a JSON-RPC request to the Bravia API."""
        self._request_id += 1
        url = f"{self._base_url}/{service}"
        payload = {
            "method": method,
            "id": self._request_id,
            "params": params if params is not None else [],
            "version": version,
        }
        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "X-Auth-PSK": self._psk,
        }

        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                async with self._session.post(
                    url, json=payload, headers=headers
                ) as resp:
                    if resp.status == 403:
                        raise BraviaAuthError(
                            f"Authentication failed for {method} "
                            f"(HTTP 403). Check your PSK."
                        )
                    if resp.status == 404:
                        raise BraviaApiError(
                            404,
                            f"Service {service}/{method} not available on this device",
                        )
                    resp.raise_for_status()
                    data = await resp.json(content_type=None)
        except BraviaError:
            raise
        except (aiohttp.ClientError, OSError) as err:
            raise BraviaConnectionError(
                f"Cannot connect to Bravia TV at {self._host}: {err}"
            ) from err
        except TimeoutError as err:
            raise BraviaConnectionError(
                f"Timeout connecting to Bravia TV at {self._host}"
            ) from err

        if "error" in data:
            error = data["error"]
            code = error[0] if isinstance(error, list) and error else 0
            msg = error[1] if isinstance(error, list) and len(error) > 1 else str(error)
            if code == 7:
                raise BraviaTurnedOffError(
                    f"TV is powered off or unavailable for {method}"
                )
            raise BraviaApiError(code, msg)

        return data.get("result", [])

    async def _send_ircc(self, ircc_code: str) -> None:
        """Send an IRCC command via SOAP."""
        url = f"{self._base_url}/IRCC"
        body = IRCC_SOAP_BODY.format(ircc_code=ircc_code)
        headers = {
            "Content-Type": "text/xml; charset=UTF-8",
            "X-Auth-PSK": self._psk,
            "SOAPACTION": IRCC_SOAP_ACTION,
        }

        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                async with self._session.post(url, data=body, headers=headers) as resp:
                    if resp.status == 403:
                        raise BraviaAuthError("Authentication failed for IRCC command")
                    resp.raise_for_status()
        except BraviaError:
            raise
        except (aiohttp.ClientError, OSError) as err:
            raise BraviaConnectionError(
                f"Cannot send IRCC to Bravia TV at {self._host}: {err}"
            ) from err
        except TimeoutError as err:
            raise BraviaConnectionError(
                f"Timeout sending IRCC to Bravia TV at {self._host}"
            ) from err

    # ------------------------------------------------------------------
    # Guide service
    # ------------------------------------------------------------------

    async def get_supported_api_info(
        self, services: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """Get supported API info for discovery."""
        params = [{"services": services}] if services else [{}]
        result = await self._request(SERVICE_GUIDE, "getSupportedApiInfo", params)
        return result[0] if result else []

    # ------------------------------------------------------------------
    # System service
    # ------------------------------------------------------------------

    async def get_system_info(self) -> dict[str, Any]:
        """Get system information (model, serial, MAC, firmware)."""
        result = await self._request(SERVICE_SYSTEM, "getSystemInformation")
        return result[0] if result else {}

    async def get_power_status(self) -> str:
        """Get power status. Returns 'active' or 'standby'."""
        result = await self._request(SERVICE_SYSTEM, "getPowerStatus")
        if result and isinstance(result[0], dict):
            return result[0].get("status", "standby")
        return "standby"

    async def set_power_status(self, status: bool) -> None:
        """Set power status. True = on, False = off."""
        await self._request(
            SERVICE_SYSTEM, "setPowerStatus", [{"status": status}]
        )

    async def get_remote_controller_info(self) -> list[dict[str, str]]:
        """Get IRCC remote controller codes."""
        result = await self._request(
            SERVICE_SYSTEM, "getRemoteControllerInfo"
        )
        # Response format varies: [[{name, value}, ...]] or [{name, value}, ...]
        if result:
            codes = result[1] if len(result) > 1 else result[0]
            if isinstance(codes, list):
                return codes
        return []

    async def get_wol_mode(self) -> bool:
        """Get Wake-on-LAN mode status."""
        result = await self._request(SERVICE_SYSTEM, "getWolMode")
        if result and isinstance(result[0], dict):
            return result[0].get("enabled", False)
        return False

    async def set_wol_mode(self, enabled: bool) -> None:
        """Set Wake-on-LAN mode."""
        await self._request(SERVICE_SYSTEM, "setWolMode", [{"enabled": enabled}])

    async def get_led_status(self) -> bool:
        """Get LED indicator status."""
        result = await self._request(SERVICE_SYSTEM, "getLEDIndicatorStatus")
        if result and isinstance(result[0], dict):
            status = result[0].get("status")
            if isinstance(status, bool):
                return status
            return status == "on"
        return False

    async def set_led_status(self, status: bool) -> None:
        """Set LED indicator status. Tries v1.1 then v1.0."""
        try:
            await self._request(
                SERVICE_SYSTEM,
                "setLEDIndicatorStatus",
                [{"status": "on" if status else "off"}],
                version="1.1",
            )
        except BraviaApiError:
            await self._request(
                SERVICE_SYSTEM,
                "setLEDIndicatorStatus",
                [{"status": status}],
                version="1.0",
            )

    async def get_power_saving_mode(self) -> str:
        """Get power saving mode."""
        result = await self._request(SERVICE_SYSTEM, "getPowerSavingMode")
        if result and isinstance(result[0], dict):
            return result[0].get("mode", "off")
        return "off"

    async def set_power_saving_mode(self, mode: str) -> None:
        """Set power saving mode (off, low, high, pictureOff)."""
        await self._request(
            SERVICE_SYSTEM, "setPowerSavingMode", [{"mode": mode}]
        )

    async def request_reboot(self) -> None:
        """Request device reboot."""
        await self._request(SERVICE_SYSTEM, "requestReboot")

    async def get_current_time(self) -> str:
        """Get device current time."""
        result = await self._request(SERVICE_SYSTEM, "getCurrentTime")
        if result and isinstance(result[0], dict):
            return result[0].get("dateTime", "")
        if result and isinstance(result[0], str):
            return result[0]
        return ""

    async def get_network_settings(self) -> list[dict[str, Any]]:
        """Get network settings."""
        result = await self._request(SERVICE_SYSTEM, "getNetworkSettings")
        return result[0] if result and isinstance(result[0], list) else result

    async def get_interface_info(self) -> dict[str, Any]:
        """Get interface information."""
        result = await self._request(SERVICE_SYSTEM, "getInterfaceInformation")
        return result[0] if result else {}

    async def get_system_supported_function(self) -> list[dict[str, Any]]:
        """Get supported system functions."""
        result = await self._request(
            SERVICE_SYSTEM, "getSystemSupportedFunction"
        )
        return result[0] if result and isinstance(result[0], list) else result

    # ------------------------------------------------------------------
    # Audio service
    # ------------------------------------------------------------------

    async def get_volume_info(self) -> list[dict[str, Any]]:
        """Get volume information for all targets."""
        result = await self._request(SERVICE_AUDIO, "getVolumeInformation")
        return result[0] if result and isinstance(result[0], list) else result

    async def set_volume(self, volume: str, target: str = "") -> None:
        """Set volume. Accepts absolute ("25") or relative ("+5", "-5")."""
        await self._request(
            SERVICE_AUDIO,
            "setAudioVolume",
            [{"target": target, "volume": volume}],
        )

    async def set_mute(self, mute: bool) -> None:
        """Set mute status."""
        await self._request(
            SERVICE_AUDIO, "setAudioMute", [{"status": mute}]
        )

    async def get_speaker_settings(
        self, target: str = ""
    ) -> list[dict[str, Any]]:
        """Get speaker settings."""
        result = await self._request(
            SERVICE_AUDIO, "getSpeakerSettings", [{"target": target}]
        )
        return result[0] if result and isinstance(result[0], list) else result

    async def set_sound_settings(
        self, settings: list[dict[str, str]]
    ) -> None:
        """Set sound settings (e.g., output terminal)."""
        await self._request(
            SERVICE_AUDIO,
            "setSoundSettings",
            [{"settings": settings}],
            version="1.1",
        )

    async def set_speaker_settings(
        self, settings: list[dict[str, str]]
    ) -> None:
        """Set speaker settings."""
        await self._request(
            SERVICE_AUDIO,
            "setSpeakerSettings",
            [{"settings": settings}],
        )

    # ------------------------------------------------------------------
    # AV Content service
    # ------------------------------------------------------------------

    async def get_playing_content(self) -> dict[str, Any]:
        """Get currently playing content info."""
        result = await self._request(
            SERVICE_AV_CONTENT, "getPlayingContentInfo"
        )
        return result[0] if result else {}

    async def set_play_content(self, uri: str) -> None:
        """Switch to content by URI (e.g., extInput:hdmi?port=1)."""
        await self._request(
            SERVICE_AV_CONTENT, "setPlayContent", [{"uri": uri}]
        )

    async def get_external_inputs(self) -> list[dict[str, Any]]:
        """Get status of external inputs (HDMI, etc.)."""
        try:
            result = await self._request(
                SERVICE_AV_CONTENT,
                "getCurrentExternalInputsStatus",
                version="1.1",
            )
        except BraviaApiError:
            result = await self._request(
                SERVICE_AV_CONTENT,
                "getCurrentExternalInputsStatus",
                version="1.0",
            )
        return result[0] if result and isinstance(result[0], list) else result

    async def get_scheme_list(self) -> list[str]:
        """Get available URI schemes."""
        result = await self._request(SERVICE_AV_CONTENT, "getSchemeList")
        if result and isinstance(result[0], list):
            return [
                item.get("scheme", item) if isinstance(item, dict) else item
                for item in result[0]
            ]
        return []

    async def get_source_list(self, scheme: str) -> list[dict[str, Any]]:
        """Get sources for a URI scheme."""
        result = await self._request(
            SERVICE_AV_CONTENT, "getSourceList", [{"scheme": scheme}]
        )
        return result[0] if result and isinstance(result[0], list) else result

    async def get_content_list(
        self,
        uri: str | None = None,
        start: int = 0,
        count: int = 50,
    ) -> list[dict[str, Any]]:
        """Get content list for a source URI."""
        params: dict[str, Any] = {"stIdx": start, "cnt": count}
        if uri is not None:
            params["uri"] = uri
        result = await self._request(
            SERVICE_AV_CONTENT, "getContentList", [params], version="1.5"
        )
        return result[0] if result and isinstance(result[0], list) else result

    # ------------------------------------------------------------------
    # App Control service
    # ------------------------------------------------------------------

    async def get_app_list(self) -> list[dict[str, Any]]:
        """Get list of installed applications."""
        result = await self._request(
            SERVICE_APP_CONTROL, "getApplicationList"
        )
        return result[0] if result and isinstance(result[0], list) else result

    async def set_active_app(self, uri: str) -> None:
        """Launch an application by URI."""
        await self._request(
            SERVICE_APP_CONTROL, "setActiveApp", [{"uri": uri}]
        )

    async def get_app_status_list(self) -> list[dict[str, str]]:
        """Get application status list (textInput, cursorDisplay, webBrowse)."""
        result = await self._request(
            SERVICE_APP_CONTROL, "getApplicationStatusList"
        )
        return result[0] if result and isinstance(result[0], list) else result

    async def get_web_app_status(self) -> dict[str, Any]:
        """Get web app status."""
        result = await self._request(
            SERVICE_APP_CONTROL, "getWebAppStatus"
        )
        return result[0] if result else {}

    async def terminate_apps(self) -> None:
        """Terminate all foreground applications."""
        await self._request(SERVICE_APP_CONTROL, "terminateApps")

    async def set_text_form(self, text: str) -> None:
        """Send text to the on-screen keyboard."""
        await self._request(
            SERVICE_APP_CONTROL, "setTextForm", [text], version="1.0"
        )

    # ------------------------------------------------------------------
    # Video service
    # ------------------------------------------------------------------

    async def get_picture_quality_settings(
        self, target: str = ""
    ) -> list[dict[str, Any]]:
        """Get picture quality settings."""
        result = await self._request(
            SERVICE_VIDEO,
            "getPictureQualitySettings",
            [{"target": target}],
        )
        return result[0] if result and isinstance(result[0], list) else result

    async def set_picture_quality_settings(
        self, settings: list[dict[str, str]]
    ) -> None:
        """Set picture quality settings."""
        await self._request(
            SERVICE_VIDEO,
            "setPictureQualitySettings",
            [{"settings": settings}],
        )

    async def get_screen_rotation(self) -> int:
        """Get screen rotation angle."""
        result = await self._request(SERVICE_VIDEO, "getScreenRotation")
        if result and isinstance(result[0], dict):
            return result[0].get("angle", 0)
        return 0

    async def set_screen_rotation(self, angle: int) -> None:
        """Set screen rotation angle (0, 90, 180, 270)."""
        await self._request(
            SERVICE_VIDEO, "setScreenRotation", [{"angle": angle}]
        )

    # ------------------------------------------------------------------
    # VideoScreen service
    # ------------------------------------------------------------------

    async def set_scene_setting(self, scene: str) -> None:
        """Set scene/picture mode setting."""
        await self._request(
            SERVICE_VIDEO_SCREEN, "setSceneSetting", [{"scene": scene}]
        )

    # ------------------------------------------------------------------
    # IRCC (infrared remote control)
    # ------------------------------------------------------------------

    async def send_ircc(self, code: str) -> None:
        """Send an IRCC remote control code."""
        await self._send_ircc(code)

    # ------------------------------------------------------------------
    # Convenience / composite methods
    # ------------------------------------------------------------------

    async def power_on(self) -> None:
        """Power on the TV."""
        await self.set_power_status(True)

    async def power_off(self) -> None:
        """Power off the TV."""
        await self.set_power_status(False)

    async def volume_up(self) -> None:
        """Increase volume by 1."""
        await self.set_volume("+1")

    async def volume_down(self) -> None:
        """Decrease volume by 1."""
        await self.set_volume("-1")

    async def is_available(self) -> bool:
        """Check if the TV is reachable."""
        try:
            await self.get_power_status()
            return True
        except BraviaError:
            return False

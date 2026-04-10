"""Sony Bravia Pro integration for Home Assistant."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .bravia_client import BraviaClient, BraviaError
from .const import CONF_PSK, DOMAIN, IRCC_CODES, POWER_SAVING_OFF, POWER_SAVING_PICTURE_OFF
from .coordinator import BraviaCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORM_LIST = [
    Platform.MEDIA_PLAYER,
    Platform.REMOTE,
    Platform.BUTTON,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]

# Service names
SERVICE_OPEN_APP = "open_app"
SERVICE_SEND_IRCC = "send_ircc"
SERVICE_SET_AUDIO_OUTPUT = "set_audio_output"
SERVICE_BLANK_SCREEN = "blank_screen"
SERVICE_GET_INSTALLED_APPS = "get_installed_apps"

# Service schemas
SERVICE_OPEN_APP_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_id,
        vol.Optional("app_name"): cv.string,
        vol.Optional("app_uri"): cv.string,
    }
)

SERVICE_SEND_IRCC_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_id,
        vol.Required("command"): cv.string,
    }
)

SERVICE_SET_AUDIO_OUTPUT_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_id,
        vol.Required("output"): vol.In(
            ["speaker", "hdmi", "speaker_hdmi", "audioSystem"]
        ),
    }
)

SERVICE_BLANK_SCREEN_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_id,
        vol.Required("enable"): cv.boolean,
    }
)

SERVICE_GET_INSTALLED_APPS_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_id,
    }
)


def _get_coordinator(hass: HomeAssistant, entity_id: str) -> BraviaCoordinator | None:
    """Find the coordinator for a given entity_id."""
    for coordinator in hass.data.get(DOMAIN, {}).values():
        if isinstance(coordinator, BraviaCoordinator):
            return coordinator
    return None


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sony Bravia Pro from a config entry."""
    host = entry.data[CONF_HOST]
    psk = entry.data[CONF_PSK]

    session = async_get_clientsession(hass)
    client = BraviaClient(host, psk, session)

    coordinator = BraviaCoordinator(hass, client, entry)
    await coordinator.async_setup()
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORM_LIST)

    # Register services (only once, on first entry)
    if not hass.services.has_service(DOMAIN, SERVICE_OPEN_APP):
        _register_services(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(
        entry, PLATFORM_LIST
    ):
        hass.data[DOMAIN].pop(entry.entry_id)

    # Remove services if no entries left
    if not hass.data.get(DOMAIN):
        for service in (
            SERVICE_OPEN_APP,
            SERVICE_SEND_IRCC,
            SERVICE_SET_AUDIO_OUTPUT,
            SERVICE_BLANK_SCREEN,
            SERVICE_GET_INSTALLED_APPS,
        ):
            hass.services.async_remove(DOMAIN, service)

    return unload_ok


def _register_services(hass: HomeAssistant) -> None:
    """Register custom services."""

    async def handle_open_app(call: ServiceCall) -> None:
        """Handle the open_app service."""
        coordinator = _get_coordinator(hass, call.data["entity_id"])
        if coordinator is None:
            _LOGGER.error("No Sony Bravia Pro device found")
            return

        app_uri = call.data.get("app_uri")
        app_name = call.data.get("app_name")

        if not app_uri and not app_name:
            _LOGGER.error("Either app_name or app_uri must be provided")
            return

        if not app_uri and app_name:
            # Look up by name (case-insensitive)
            name_lower = app_name.lower()
            if coordinator.data and coordinator.data.app_list:
                for app in coordinator.data.app_list:
                    if app.get("title", "").lower() == name_lower:
                        app_uri = app.get("uri")
                        break
            if not app_uri:
                _LOGGER.error(
                    "App '%s' not found. Available: %s",
                    app_name,
                    ", ".join(
                        a.get("title", "?")
                        for a in (coordinator.data.app_list if coordinator.data else [])
                    ),
                )
                return

        try:
            await coordinator.client.set_active_app(app_uri)
        except BraviaError as err:
            _LOGGER.error("Failed to open app: %s", err)

    async def handle_send_ircc(call: ServiceCall) -> None:
        """Handle the send_ircc service."""
        coordinator = _get_coordinator(hass, call.data["entity_id"])
        if coordinator is None:
            _LOGGER.error("No Sony Bravia Pro device found")
            return

        command = call.data["command"]

        try:
            if command.endswith("==") or command.endswith("Aw=="):
                # Raw base64 IRCC code
                await coordinator.client.send_ircc(command)
            else:
                # Try TV-discovered codes first, then predefined fallback
                code = coordinator.ircc_codes.get(command) or IRCC_CODES.get(command)
                if code is None:
                    _LOGGER.error(
                        "Unknown IRCC command '%s'. Available: %s",
                        command,
                        ", ".join(sorted(
                            set(coordinator.ircc_codes.keys()) | set(IRCC_CODES.keys())
                        )),
                    )
                    return
                await coordinator.client.send_ircc(code)
        except BraviaError as err:
            _LOGGER.error("Failed to send IRCC command '%s': %s", command, err)

    async def handle_set_audio_output(call: ServiceCall) -> None:
        """Handle the set_audio_output service."""
        coordinator = _get_coordinator(hass, call.data["entity_id"])
        if coordinator is None:
            _LOGGER.error("No Sony Bravia Pro device found")
            return

        output = call.data["output"]
        try:
            await coordinator.client.set_sound_settings(
                [{"target": "outputTerminal", "value": output}]
            )
        except BraviaError as err:
            _LOGGER.error("Failed to set audio output to '%s': %s", output, err)

    async def handle_blank_screen(call: ServiceCall) -> None:
        """Handle the blank_screen service."""
        coordinator = _get_coordinator(hass, call.data["entity_id"])
        if coordinator is None:
            _LOGGER.error("No Sony Bravia Pro device found")
            return

        enable = call.data["enable"]
        mode = POWER_SAVING_PICTURE_OFF if enable else POWER_SAVING_OFF
        try:
            await coordinator.client.set_power_saving_mode(mode)
        except BraviaError as err:
            _LOGGER.error("Failed to set blank screen: %s", err)

    async def handle_get_installed_apps(call: ServiceCall) -> None:
        """Handle the get_installed_apps service."""
        coordinator = _get_coordinator(hass, call.data["entity_id"])
        if coordinator is None:
            _LOGGER.error("No Sony Bravia Pro device found")
            return

        await coordinator.refresh_app_list()
        _LOGGER.info(
            "App list refreshed. %d apps found.",
            len(coordinator.data.app_list) if coordinator.data else 0,
        )

    hass.services.async_register(
        DOMAIN, SERVICE_OPEN_APP, handle_open_app, schema=SERVICE_OPEN_APP_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SEND_IRCC, handle_send_ircc, schema=SERVICE_SEND_IRCC_SCHEMA
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_AUDIO_OUTPUT,
        handle_set_audio_output,
        schema=SERVICE_SET_AUDIO_OUTPUT_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_BLANK_SCREEN,
        handle_blank_screen,
        schema=SERVICE_BLANK_SCREEN_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_INSTALLED_APPS,
        handle_get_installed_apps,
        schema=SERVICE_GET_INSTALLED_APPS_SCHEMA,
    )

"""Sony Bravia Pro integration for Home Assistant."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .bravia_client import BraviaClient
from .const import CONF_PSK, DOMAIN, PLATFORMS
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

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(
        entry, PLATFORM_LIST
    ):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

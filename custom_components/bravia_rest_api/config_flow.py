"""Config flow for Bravia REST API integration."""

from __future__ import annotations

import html
import logging
from typing import Any
from urllib.parse import urlparse

import aiohttp
import voluptuous as vol

from homeassistant.components import ssdp
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_HOST
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig

from .bravia_client import (
    BraviaAuthError,
    BraviaClient,
    BraviaConnectionError,
    BraviaError,
)
from .const import CONF_EXCLUDED_SOURCES, CONF_MAC, CONF_PSK, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PSK): str,
    }
)


class BraviaRestApiConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Bravia REST API."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Create the options flow."""
        return BraviaRestApiOptionsFlow()

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_host: str | None = None
        self._discovered_model: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step: ask for IP and PSK."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            psk = user_input[CONF_PSK]

            session = async_get_clientsession(self.hass)
            client = BraviaClient(host, psk, session)

            try:
                system_info = await client.get_system_info()
            except BraviaAuthError:
                errors["base"] = "invalid_auth"
            except BraviaConnectionError:
                errors["base"] = "cannot_connect"
            except BraviaError:
                errors["base"] = "cannot_connect"
            else:
                model = system_info.get("model")
                if not model:
                    errors["base"] = "cannot_connect"
                else:
                    serial = system_info.get("serial", "")
                    mac = system_info.get("macAddr", "")
                    name = system_info.get("name", model)
                    firmware = system_info.get("generation", "")

                    unique_id = serial or mac or host
                    await self.async_set_unique_id(unique_id)
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=name or model,
                        data={
                            CONF_HOST: host,
                            CONF_PSK: psk,
                            CONF_MAC: mac,
                            "model": model,
                            "serial": serial,
                            "firmware": firmware,
                        },
                    )

        # Pre-fill host if discovered via SSDP
        schema = STEP_USER_DATA_SCHEMA
        if self._discovered_host:
            schema = vol.Schema(
                {
                    vol.Required(CONF_HOST, default=self._discovered_host): str,
                    vol.Required(CONF_PSK): str,
                }
            )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
            description_placeholders={"model": self._discovered_model or ""},
        )

    async def async_step_ssdp(
        self, discovery_info: ssdp.SsdpServiceInfo
    ) -> ConfigFlowResult:
        """Handle SSDP discovery of a Sony Bravia TV."""
        # Extract host from SSDP location URL
        location = discovery_info.ssdp_location or ""
        parsed = urlparse(location)
        host = parsed.hostname or ""

        if not host:
            return self.async_abort(reason="cannot_connect")

        _LOGGER.info(
            "Discovered Sony Bravia TV via SSDP at %s: %s",
            host,
            discovery_info.upnp.get(ssdp.ATTR_UPNP_FRIENDLY_NAME, "Unknown"),
        )

        # Try to get system info to find unique_id
        session = async_get_clientsession(self.hass)
        # Try without PSK for read-only endpoints
        client = BraviaClient(host, "", session)

        try:
            system_info = await client.get_system_info()
            serial = system_info.get("serial", "")
            mac = system_info.get("macAddr", "")
            model = system_info.get("model", "")
            unique_id = serial or mac or host
        except BraviaError:
            # System info may require PSK — use host as fallback
            unique_id = host
            model = discovery_info.upnp.get(
                ssdp.ATTR_UPNP_MODEL_NAME, "Sony Bravia"
            )

        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured(updates={CONF_HOST: host})

        self._discovered_host = host
        self._discovered_model = model

        self.context["title_placeholders"] = {"name": model or host}

        return await self.async_step_user()


class BraviaRestApiOptionsFlow(OptionsFlow):
    """Handle options for Bravia REST API."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            excluded = user_input.get(CONF_EXCLUDED_SOURCES, [])
            if isinstance(excluded, str):
                # Text area fallback: split by newlines
                excluded = [s.strip() for s in excluded.splitlines() if s.strip()]
            return self.async_create_entry(
                title="", data={CONF_EXCLUDED_SOURCES: excluded}
            )

        # Build available sources from coordinator
        coordinator = self.hass.data.get(DOMAIN, {}).get(
            self.config_entry.entry_id
        )
        sources: list[str] = []
        if coordinator and coordinator.data:
            data = coordinator.data
            for inp in data.external_inputs:
                custom_label = inp.get("label", "")
                label = inp.get("title", "")
                name = custom_label if custom_label else label
                if name:
                    sources.append(name)
            for app in data.app_list:
                title = html.unescape(app.get("title", ""))
                if title:
                    sources.append(title)

        current_excluded = self.config_entry.options.get(
            CONF_EXCLUDED_SOURCES, []
        )

        if sources:
            # Multi-select with current sources
            source_lower_map = {s.lower(): s for s in sources}
            valid_default = [
                source_lower_map[e.lower()]
                for e in current_excluded
                if e.lower() in source_lower_map
            ]
            schema = vol.Schema(
                {
                    vol.Optional(
                        CONF_EXCLUDED_SOURCES, default=valid_default
                    ): cv.multi_select({s: s for s in sorted(sources)}),
                }
            )
        else:
            # TV off fallback: multiline text input
            schema = vol.Schema(
                {
                    vol.Optional(
                        CONF_EXCLUDED_SOURCES,
                        default="\n".join(current_excluded),
                    ): TextSelector(TextSelectorConfig(multiline=True)),
                }
            )

        return self.async_show_form(step_id="init", data_schema=schema)

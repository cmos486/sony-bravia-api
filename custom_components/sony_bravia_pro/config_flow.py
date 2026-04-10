"""Config flow for Sony Bravia Pro integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .bravia_client import (
    BraviaAuthError,
    BraviaClient,
    BraviaConnectionError,
    BraviaError,
)
from .const import CONF_MAC, CONF_PSK, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PSK): str,
    }
)


class SonyBraviaProConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sony Bravia Pro."""

    VERSION = 1

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
                power_status = await client.get_power_status()
            except BraviaAuthError:
                errors["base"] = "invalid_auth"
            except BraviaConnectionError:
                errors["base"] = "cannot_connect"
            except BraviaError:
                errors["base"] = "cannot_connect"
            else:
                if power_status != "active":
                    errors["base"] = "tv_off"
                else:
                    serial = system_info.get("serial", "")
                    model = system_info.get("model", "Sony Bravia Pro")
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

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

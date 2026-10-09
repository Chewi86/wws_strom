"""Config Flow für WestfalenWIND Stromtarif."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import AUTH_ENDPOINT, CONF_PASSWORD, CONF_USERNAME, DOMAIN


async def validate_input(hass, data):
    """Validiert die Zugangsdaten gegen die API."""

    def _login():
        payload = urllib.parse.urlencode(
            {
                "grant_type": "password",
                "username": data[CONF_USERNAME],
                "password": data[CONF_PASSWORD],
            }
        ).encode("utf-8")

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        req = urllib.request.Request(
            AUTH_ENDPOINT, data=payload, headers=headers, method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = response.read().decode("utf-8")
            res_data = json.loads(res_body)
            if not (
                res_data.get("access_token") or res_data.get("token")
            ):
                raise ValueError("Kein Token in der Antwort enthalten")

    await hass.async_add_executor_job(_login)


class WWSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow zur Einrichtung der WWS Integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Erster Schritt bei der Einrichtung."""
        errors = {}

        if user_input is not None:
            try:
                await validate_input(self.hass, user_input)
                return self.async_create_entry(
                    title=f"WWS ({user_input[CONF_USERNAME]})",
                    data=user_input,
                )
            except Exception:
                errors["base"] = "invalid_auth"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
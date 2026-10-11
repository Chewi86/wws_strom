# """Config Flow für WestfalenWIND Stromtarif."""

# from __future__ import annotations

# import json
# import urllib.parse
# import urllib.request
# import voluptuous as vol

# from homeassistant import config_entries
# from homeassistant.data_entry_flow import FlowResult

# from .const import AUTH_ENDPOINT, CONF_PASSWORD, CONF_USERNAME, DOMAIN


# async def validate_input(hass, data):
    # """Validiert die Zugangsdaten gegen die API."""

    # def _login():
        # payload = urllib.parse.urlencode(
            # {
                # "grant_type": "password",
                # "username": data[CONF_USERNAME],
                # "password": data[CONF_PASSWORD],
            # }
        # ).encode("utf-8")

        # headers = {
            # "Content-Type": "application/x-www-form-urlencoded",
            # "Accept": "application/json",
        # }

        # req = urllib.request.Request(
            # AUTH_ENDPOINT, data=payload, headers=headers, method="POST"
        # )
        # with urllib.request.urlopen(req, timeout=10) as response:
            # res_body = response.read().decode("utf-8")
            # res_data = json.loads(res_body)
            # if not (
                # res_data.get("access_token") or res_data.get("token")
            # ):
                # raise ValueError("Kein Token in der Antwort enthalten")

    # await hass.async_add_executor_job(_login)


# class WWSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    # """Config Flow zur Einrichtung der WWS Integration."""

    # VERSION = 1

    # async def async_step_user(self, user_input=None) -> FlowResult:
        # """Erster Schritt bei der Einrichtung."""
        # errors = {}

        # if user_input is not None:
            # try:
                # await validate_input(self.hass, user_input)
                # return self.async_create_entry(
                    # title=f"WWS ({user_input[CONF_USERNAME]})",
                    # data=user_input,
                # )
            # except Exception:
                # errors["base"] = "invalid_auth"

        # data_schema = vol.Schema(
            # {
                # vol.Required(CONF_USERNAME): str,
                # vol.Required(CONF_PASSWORD): str,
            # }
        # )

        # return self.async_show_form(
            # step_id="user", data_schema=data_schema, errors=errors
        # )
        
"""Config Flow für WestfalenWIND Strom."""

from __future__ import annotations

import json
import logging
import urllib.parse
import urllib.request
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import AUTH_ENDPOINT, CONF_PASSWORD, CONF_USERNAME, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


async def async_validate_input(hass: HomeAssistant, data: dict) -> dict:
    """Validiert die Zugangsdaten durch einen Test-Login an der WWS-API."""
    def _test_login():
        payload = urllib.parse.urlencode({
            "grant_type": "password",
            "username": data[CONF_USERNAME],
            "password": data[CONF_PASSWORD],
        }).encode("utf-8")

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        req = urllib.request.Request(AUTH_ENDPOINT, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            token = res_data.get("access_token") or res_data.get("token")
            if not token:
                raise ValueError("Kein Token erhalten.")
            return token

    try:
        await hass.async_add_executor_job(_test_login)
    except Exception as err:
        _LOGGER.error("Authentifizierungsfehler bei WWS-API: %s", err)
        raise InvalidAuth from err

    return {"title": f"WestfalenWIND ({data[CONF_USERNAME]})"}


class WWSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow für WWS Strom."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Behandelt den ersten Schritt des Config Flows."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await async_validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class InvalidAuth(HomeAssistantError):
    """Fehler bei ungültigen Zugangsdaten."""
import voluptuous as vol
import logging

from gkeepapi import Keep
from gkeepapi.exception import LoginException
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResult

import homeassistant.helpers.config_validation as cv

from .const import CONF_LIST_NAME, DEFAULT_LIST_NAME, DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__package__)

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_LIST_NAME, default=DEFAULT_LIST_NAME): cv.string,
    }
)


class GoogleKeepConfigFlow(ConfigFlow, domain=DOMAIN):
    """The configuration flow for a Google Keep list."""

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}
        if user_input:
            try:
                keep = Keep()

                await self.hass.async_add_executor_job(
                    lambda: keep.login(user_input[CONF_EMAIL], user_input[CONF_PASSWORD])
                )

                master_token: str = await self.hass.async_add_executor_job(
                    lambda: keep.getMasterToken()
                )

                if master_token:
                    # Make sure we're not configuring the same list
                    await self.async_set_unique_id(
                        f"gkeep_sync_{user_input[CONF_LIST_NAME]}"
                    )
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=f"Google Keep ({user_input[CONF_LIST_NAME]})",
                        data=user_input,
                    )
            except LoginException:
                errors[CONF_PASSWORD] = "invalid_credentials"
            else:
                errors[CONF_EMAIL] = "unknown_error"

        return self.async_show_form(
            step_id="user", data_schema=CONFIG_SCHEMA, errors=errors
        )

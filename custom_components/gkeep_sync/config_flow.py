import voluptuous as vol
import logging

from gkeepapi import Keep
from gkeepapi.exception import LoginException
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResult

import homeassistant.helpers.config_validation as cv

from .const import CONF_MASTER_TOKEN, DOMAIN

_LOGGER: logging.Logger = logging.getLogger(__package__)

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): cv.string,
        vol.Optional(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_MASTER_TOKEN): cv.string,
    }
)


class GoogleKeepConfigFlow(ConfigFlow, domain=DOMAIN):
    """The configuration flow for a Google Keep list."""

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}
        if user_input:
            if (
                user_input.get(CONF_MASTER_TOKEN) is None
                and user_input.get(CONF_PASSWORD) is None
            ):
                errors[CONF_PASSWORD] = "credentials_required"
            else:
                try:
                    keep = Keep()

                    if user_input.get(CONF_MASTER_TOKEN) is not None:
                        await self.hass.async_add_executor_job(
                            lambda: keep.resume(
                                user_input[CONF_EMAIL], user_input.get(CONF_MASTER_TOKEN)
                            )
                        )
                    else:
                        await self.hass.async_add_executor_job(
                            lambda: keep.login(
                                user_input[CONF_EMAIL], user_input.get(CONF_PASSWORD)
                            )
                        )

                    master_token: str = await self.hass.async_add_executor_job(
                        lambda: keep.getMasterToken()
                    )

                    if master_token:
                        # Make sure we're not configuring the same list
                        await self.async_set_unique_id(
                            f"gkeep_sync_{user_input[CONF_EMAIL]}"
                        )
                        self._abort_if_unique_id_configured()

                        return self.async_create_entry(
                            title=f"Google Keep ({user_input[CONF_EMAIL]})",
                            data=user_input,
                        )
                except LoginException:
                    errors[CONF_EMAIL] = "invalid_credentials"
                else:
                    errors[CONF_EMAIL] = "unknown_error"

        return self.async_show_form(
            step_id="user", data_schema=CONFIG_SCHEMA, errors=errors
        )

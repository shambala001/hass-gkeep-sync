"""The Google Keep integration"""

import logging

from gkeepapi import Keep
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, Platform

from homeassistant.core import HomeAssistant

from . import api
from .const import (
    DOMAIN,
    DEFAULT_LIST_NAME,
    CONF_MASTER_TOKEN,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.TODO]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Google Tasks from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    keep: Keep = Keep()

    auth = api.AsyncConfigEntryAuth(
        hass,
        keep,
        email=entry.data.get(CONF_EMAIL),
        password=entry.data.get(CONF_PASSWORD),
        token=entry.data.get(CONF_MASTER_TOKEN),
    )

    await auth.async_get_access_token()

    hass.data[DOMAIN][entry.entry_id] = auth

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

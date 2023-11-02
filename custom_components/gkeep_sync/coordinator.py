"""Coordinator for fetching data from Google Keep API."""

import asyncio
import datetime
import logging
from typing import Any, Final

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import AsyncConfigEntryAuth

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL: Final = datetime.timedelta(minutes=30)
TIMEOUT = 10


class TaskUpdateCoordinator(DataUpdateCoordinator[list[dict[str, Any]]]):
    """Coordinator for fetching Google Keep tasks for a Task List from the API."""

    def __init__(
        self, hass: HomeAssistant, api: AsyncConfigEntryAuth, task_list_name: str
    ) -> None:
        """Initialize TaskUpdateCoordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"Google Keep ({task_list_name})",
            update_interval=UPDATE_INTERVAL,
        )
        self.api = api
        self._task_list_name = task_list_name

    async def _async_update_data(self) -> list[dict[str, Any]]:
        """Fetch tasks from API endpoint."""
        async with asyncio.timeout(TIMEOUT):
            return await self.api.list_tasks(self._task_list_name)

"""API for Google Keep."""
from __future__ import annotations

import logging
from typing import Any

from gkeepapi import Keep
from gkeepapi.node import List, NodeType
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class AsyncConfigEntryAuth:
    def __init__(
        self,
        hass: HomeAssistant,
        keep: Keep,
        email: str,
        password: str | None = None,
        token: str | None = None,
    ) -> None:
        """Initialize Google Keep Auth."""
        self._hass = hass
        self._email = email
        self._password = password
        self._keep = keep
        self._token = token

    async def async_get_access_token(self):
        if not self._token:
            await self._hass.async_add_executor_job(
                lambda: self._keep.login(self._email, self._password)
            )
            self._token = self._keep.getMasterToken()
            self._password = None

        return self._token

    async def _get_service(self) -> Keep:
        """Get current resource."""
        token = await self.async_get_access_token()
        await self._hass.async_add_executor_job(
            lambda: self._keep.resume(self._email, token)
        )

        return self._keep

    async def list_task_lists(self) -> list[dict[str, Any]]:
        """Get all Task List resources."""
        service = await self._get_service()
        lists: list[dict[str, Any]] = []

        keep_notes = await self._hass.async_add_executor_job(lambda: service.all())

        for note in keep_notes:
            if (
                note.type == NodeType.List
                and note.title != ""
                and note.archived is False
            ):
                lists.append({"id": note.title, "title": note.title})

        _LOGGER.debug("Found %s lists", len(lists))

        return lists

    async def list_tasks(self, task_list_name: str) -> list[dict[str, Any]]:
        """Get all Task resources for the task list."""
        tasks: list[dict[str, Any]] = []
        task_list: List = await self._get_or_create_list_name(task_list_name)

        for item in task_list.items:
            tasks.append({"id": item.text, "title": item.text, "status": item.checked})

        _LOGGER.debug("Found %s tasks for list %s", len(tasks), task_list_name)

        return tasks

    async def insert(
        self,
        task_list_name: str,
        task: dict[str, Any],
    ) -> None:
        """Add items to a Google Keep list."""
        service = await self._get_service()

        list_to_update = await self._get_or_create_list_name(task_list_name, service)

        item = task["title"]

        for old_item in list_to_update.items:
            if old_item.text.lower() == item.lower():
                old_item.checked = False
                break
        else:
            list_to_update.add(item, False)

        await self._hass.async_add_executor_job(lambda: service.sync())

    async def patch(
        self,
        task_list_name: str,
        task_name: str,
        task: dict[str, Any],
    ) -> None:
        """Update a task resource."""
        service = await self._get_service()

        list_to_update = await self._get_or_create_list_name(task_list_name, service)

        for old_item in list_to_update.items:
            if old_item.text.lower() == task_name.lower():
                old_item.text = task["title"]
                old_item.checked = task["status"] or False
                break

        await self._hass.async_add_executor_job(lambda: service.sync())

    async def _get_or_create_list_name(
        self, list_name: str, service: Keep | None = None
    ) -> List:
        """Find the target list amongst all the Keep notes/lists"""
        if service is None:
            service = await self._hass.async_add_executor_job(
                lambda: self._get_service()
            )

        await self._hass.async_add_executor_job(lambda: service.sync())

        keep_lists = await self._hass.async_add_executor_job(lambda: service.all())

        for keep_list in keep_lists:
            if keep_list.title == list_name:
                list_object = keep_list
                break
        else:
            _LOGGER.info(
                "List with name {} not found on Keep. Creating new list.".format(
                    list_name
                )
            )
            list_object = await self._hass.async_add_executor_job(
                lambda: service.createList(list_name)
            )

        return list_object

from __future__ import annotations

import asyncio
import logging
from typing import Callable

from app.checker import VFSChecker
from app.models import CheckResult
from app.notifier import notify_slots_found

logger = logging.getLogger(__name__)

CHECK_INTERVAL_SECONDS = 60


class SlotMonitor:
    def __init__(
        self,
        checker: VFSChecker,
        on_result: Callable[[CheckResult], None] | None = None,
    ):
        self._checker = checker
        self._on_result = on_result
        self._running = False
        self._task: asyncio.Task | None = None
        self._previous_slot_keys: set[str] = set()

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def result(self) -> CheckResult:
        return self._checker.result

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("Мониторинг запущен (интервал %d сек)", CHECK_INTERVAL_SECONDS)

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
        logger.info("Мониторинг остановлен")

    async def _loop(self) -> None:
        while self._running:
            try:
                result = await self._checker.check_slots()

                new_keys = {f"{s.city.value}:{s.date}:{s.time}" for s in result.slots}
                fresh_slots = new_keys - self._previous_slot_keys

                if fresh_slots and result.slots:
                    fresh = [
                        s for s in result.slots
                        if f"{s.city.value}:{s.date}:{s.time}" in fresh_slots
                    ]
                    notify_slots_found(fresh)

                self._previous_slot_keys = new_keys

                if self._on_result:
                    self._on_result(result)

            except Exception as e:
                logger.error("Ошибка в цикле мониторинга: %s", e)

            await asyncio.sleep(CHECK_INTERVAL_SECONDS)

from __future__ import annotations

import asyncio
import logging
import re
from datetime import datetime

from app.models import (
    CITY_KEYWORDS,
    VFS_BOOKING_URL,
    CheckResult,
    CheckStatus,
    City,
    SlotInfo,
)

logger = logging.getLogger(__name__)

DATE_PATTERN_DMY = re.compile(r"\b(\d{2}\.\d{2}\.\d{4})\b")
DATE_PATTERN_ISO = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
TIME_PATTERN = re.compile(r"\b(\d{2}:\d{2})\b")

NO_SLOTS_KEYWORDS = [
    "нет доступных",
    "no available",
    "unavailable",
    "недоступно",
    "нет свободных",
    "no slots",
    "currently no",
]


def _detect_city(text: str) -> City | None:
    lower = text.lower()
    for city, keywords in CITY_KEYWORDS.items():
        for kw in keywords:
            if kw in lower:
                return city
    return None


def _extract_dates(text: str) -> list[str]:
    dates: list[str] = []
    for match in DATE_PATTERN_DMY.finditer(text):
        raw = match.group(1)
        parts = raw.split(".")
        dates.append(f"{parts[2]}-{parts[1]}-{parts[0]}")
    for match in DATE_PATTERN_ISO.finditer(text):
        dates.append(match.group(1))
    return dates


def _extract_times(text: str) -> list[str]:
    return TIME_PATTERN.findall(text)


def _has_negative_context(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in NO_SLOTS_KEYWORDS)


def parse_slots_from_snapshot(text: str) -> list[SlotInfo]:
    if not text.strip():
        return []

    slots: list[SlotInfo] = []
    lines = text.strip().splitlines()

    current_city: City | None = None
    city_block_lines: list[str] = []

    def _flush_block():
        nonlocal current_city, city_block_lines
        if current_city is None or not city_block_lines:
            city_block_lines = []
            return

        block_text = "\n".join(city_block_lines)
        if _has_negative_context(block_text):
            city_block_lines = []
            current_city = None
            return

        dates = _extract_dates(block_text)
        times = _extract_times(block_text)

        if dates:
            for i, date in enumerate(dates):
                time_val = times[i] if i < len(times) else None
                slots.append(SlotInfo(city=current_city, date=date, time=time_val))
        city_block_lines = []

    for line in lines:
        detected = _detect_city(line)
        if detected is not None:
            _flush_block()
            current_city = detected
            city_block_lines = [line]
        elif current_city is not None:
            city_block_lines.append(line)

    _flush_block()
    return slots


class VFSChecker:
    def __init__(self, headless: bool = False):
        self._headless = headless
        self._result = CheckResult()
        self._browser = None
        self._page = None
        self._lock = asyncio.Lock()

    @property
    def result(self) -> CheckResult:
        return self._result

    async def start_browser(self) -> None:
        try:
            from playwright.async_api import async_playwright

            self._pw = await async_playwright().start()
            self._browser = await self._pw.chromium.launch(
                headless=self._headless,
                args=["--disable-blink-features=AutomationControlled"],
            )
            context = await self._browser.new_context(
                locale="ru-RU",
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/131.0.0.0 Safari/537.36"
                ),
            )
            self._page = await context.new_page()
            logger.info("Браузер запущен. Переход на %s", VFS_BOOKING_URL)
            await self._page.goto(VFS_BOOKING_URL, wait_until="domcontentloaded", timeout=30000)
            self._result.status = CheckStatus.WAITING_FOR_AUTH
        except Exception as e:
            logger.error("Ошибка запуска браузера: %s", e)
            self._result.status = CheckStatus.ERROR
            self._result.error_message = str(e)

    async def check_slots(self) -> CheckResult:
        async with self._lock:
            if self._page is None:
                self._result.status = CheckStatus.ERROR
                self._result.error_message = "Браузер не запущен"
                return self._result

            self._result.status = CheckStatus.CHECKING
            try:
                await self._page.reload(wait_until="domcontentloaded", timeout=30000)
                await self._page.wait_for_timeout(3000)

                snapshot = await self._page.content()
                text_content = await self._page.evaluate("() => document.body.innerText")

                slots = parse_slots_from_snapshot(text_content)
                self._result.slots = slots
                self._result.last_check = datetime.now()
                self._result.status = CheckStatus.OK
                self._result.error_message = None

                if slots:
                    logger.info("Найдено %d слотов!", len(slots))
                else:
                    logger.info("Слоты не найдены")

            except Exception as e:
                logger.error("Ошибка проверки: %s", e)
                self._result.status = CheckStatus.ERROR
                self._result.error_message = str(e)
                self._result.last_check = datetime.now()

            return self._result

    async def close(self) -> None:
        if self._browser:
            await self._browser.close()
        if hasattr(self, "_pw") and self._pw:
            await self._pw.stop()
        self._browser = None
        self._page = None

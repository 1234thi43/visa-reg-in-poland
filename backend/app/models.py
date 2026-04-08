from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class City(str, Enum):
    PINSK = "Пинск"
    BARANOVICHI = "Барановичи"


VFS_BOOKING_URL = "https://visa.vfsglobal.com/blr/ru/pol/book-an-appointment"

CITY_KEYWORDS: dict[City, list[str]] = {
    City.PINSK: ["пинск", "pinsk"],
    City.BARANOVICHI: ["барановичи", "baranovichi", "baranovic"],
}


class SlotInfo(BaseModel):
    city: City
    date: str = Field(description="Дата слота (YYYY-MM-DD или текстовое описание)")
    time: str | None = Field(default=None, description="Время слота, если доступно")
    details: str = Field(default="", description="Дополнительные детали")

    @property
    def display_label(self) -> str:
        parts = [f"{self.city.value}: {self.date}"]
        if self.time:
            parts.append(self.time)
        if self.details:
            parts.append(f"({self.details})")
        return " ".join(parts)


class CheckStatus(str, Enum):
    IDLE = "idle"
    CHECKING = "checking"
    WAITING_FOR_AUTH = "waiting_for_auth"
    OK = "ok"
    ERROR = "error"


class CheckResult(BaseModel):
    status: CheckStatus = CheckStatus.IDLE
    slots: list[SlotInfo] = Field(default_factory=list)
    last_check: datetime | None = None
    error_message: str | None = None

    def slots_for_city(self, city: City) -> list[SlotInfo]:
        return [s for s in self.slots if s.city == city]

    @property
    def has_slots(self) -> bool:
        return len(self.slots) > 0


class StatusResponse(BaseModel):
    status: CheckStatus
    last_check: datetime | None
    error_message: str | None = None
    is_monitoring: bool = False


class SlotsResponse(BaseModel):
    slots: list[SlotInfo]
    last_check: datetime | None
    status: CheckStatus

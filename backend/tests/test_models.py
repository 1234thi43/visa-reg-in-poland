from datetime import datetime

from app.models import (
    CheckResult,
    CheckStatus,
    City,
    SlotInfo,
    SlotsResponse,
    StatusResponse,
    CITY_KEYWORDS,
)


class TestCity:
    def test_city_values(self):
        assert City.PINSK.value == "Пинск"
        assert City.BARANOVICHI.value == "Барановичи"

    def test_city_keywords_exist(self):
        assert City.PINSK in CITY_KEYWORDS
        assert City.BARANOVICHI in CITY_KEYWORDS
        assert "пинск" in CITY_KEYWORDS[City.PINSK]
        assert "барановичи" in CITY_KEYWORDS[City.BARANOVICHI]


class TestSlotInfo:
    def test_basic_creation(self):
        slot = SlotInfo(city=City.PINSK, date="2026-04-15")
        assert slot.city == City.PINSK
        assert slot.date == "2026-04-15"
        assert slot.time is None
        assert slot.details == ""

    def test_with_time_and_details(self):
        slot = SlotInfo(
            city=City.BARANOVICHI,
            date="2026-05-01",
            time="10:00",
            details="Шенгенская виза",
        )
        assert slot.time == "10:00"
        assert slot.details == "Шенгенская виза"

    def test_display_label_minimal(self):
        slot = SlotInfo(city=City.PINSK, date="2026-04-15")
        assert slot.display_label == "Пинск: 2026-04-15"

    def test_display_label_full(self):
        slot = SlotInfo(
            city=City.BARANOVICHI,
            date="2026-05-01",
            time="10:00",
            details="Шенген",
        )
        assert slot.display_label == "Барановичи: 2026-05-01 10:00 (Шенген)"


class TestCheckResult:
    def test_default_state(self):
        result = CheckResult()
        assert result.status == CheckStatus.IDLE
        assert result.slots == []
        assert result.last_check is None
        assert result.has_slots is False

    def test_with_slots(self):
        slots = [
            SlotInfo(city=City.PINSK, date="2026-04-15"),
            SlotInfo(city=City.BARANOVICHI, date="2026-04-16"),
            SlotInfo(city=City.PINSK, date="2026-04-17"),
        ]
        result = CheckResult(
            status=CheckStatus.OK,
            slots=slots,
            last_check=datetime(2026, 4, 8, 12, 0, 0),
        )
        assert result.has_slots is True
        assert len(result.slots) == 3

    def test_slots_for_city_filtering(self):
        slots = [
            SlotInfo(city=City.PINSK, date="2026-04-15"),
            SlotInfo(city=City.BARANOVICHI, date="2026-04-16"),
            SlotInfo(city=City.PINSK, date="2026-04-17"),
        ]
        result = CheckResult(status=CheckStatus.OK, slots=slots)

        pinsk = result.slots_for_city(City.PINSK)
        assert len(pinsk) == 2
        assert all(s.city == City.PINSK for s in pinsk)

        barano = result.slots_for_city(City.BARANOVICHI)
        assert len(barano) == 1
        assert barano[0].date == "2026-04-16"

    def test_error_state(self):
        result = CheckResult(
            status=CheckStatus.ERROR,
            error_message="Cloudflare block",
        )
        assert result.status == CheckStatus.ERROR
        assert result.error_message == "Cloudflare block"
        assert result.has_slots is False


class TestStatusResponse:
    def test_serialization(self):
        resp = StatusResponse(
            status=CheckStatus.CHECKING,
            last_check=datetime(2026, 4, 8, 12, 0, 0),
            is_monitoring=True,
        )
        data = resp.model_dump()
        assert data["status"] == "checking"
        assert data["is_monitoring"] is True


class TestSlotsResponse:
    def test_serialization(self):
        resp = SlotsResponse(
            slots=[SlotInfo(city=City.PINSK, date="2026-04-15")],
            last_check=datetime(2026, 4, 8, 12, 0, 0),
            status=CheckStatus.OK,
        )
        data = resp.model_dump()
        assert len(data["slots"]) == 1
        assert data["slots"][0]["city"] == "Пинск"

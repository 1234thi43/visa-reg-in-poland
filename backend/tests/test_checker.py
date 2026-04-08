import pytest

from app.checker import VFSChecker, parse_slots_from_snapshot
from app.models import CheckStatus, City


class TestParseSlots:
    def test_no_slots_in_empty_text(self):
        slots = parse_slots_from_snapshot("")
        assert slots == []

    def test_no_slots_in_irrelevant_text(self):
        text = "Добро пожаловать в визовый центр. Пожалуйста, войдите."
        slots = parse_slots_from_snapshot(text)
        assert slots == []

    def test_parse_pinsk_slot(self):
        text = """
        Пинск
        Доступные даты: 15.04.2026
        Записаться
        """
        slots = parse_slots_from_snapshot(text)
        assert len(slots) >= 1
        assert any(s.city == City.PINSK for s in slots)

    def test_parse_baranovichi_slot(self):
        text = """
        Барановичи
        Доступные даты: 20.04.2026
        Записаться
        """
        slots = parse_slots_from_snapshot(text)
        assert len(slots) >= 1
        assert any(s.city == City.BARANOVICHI for s in slots)

    def test_parse_both_cities(self):
        text = """
        Пинск - Доступно: 15.04.2026, 16.04.2026
        Барановичи - Доступно: 20.04.2026
        """
        slots = parse_slots_from_snapshot(text)
        pinsk = [s for s in slots if s.city == City.PINSK]
        barano = [s for s in slots if s.city == City.BARANOVICHI]
        assert len(pinsk) >= 1
        assert len(barano) >= 1

    def test_parse_no_available_text(self):
        text = """
        Пинск - Нет доступных дат
        Барановичи - Нет доступных дат
        """
        slots = parse_slots_from_snapshot(text)
        assert slots == []

    def test_parse_english_date_format(self):
        text = """
        Pinsk
        Available dates: 2026-04-15
        Book now
        """
        slots = parse_slots_from_snapshot(text)
        assert len(slots) >= 1
        assert any(s.city == City.PINSK for s in slots)

    def test_parse_slot_with_time(self):
        text = """
        Пинск
        15.04.2026 10:00
        15.04.2026 14:30
        """
        slots = parse_slots_from_snapshot(text)
        assert len(slots) >= 1


class TestVFSChecker:
    def test_initial_state(self):
        checker = VFSChecker(headless=True)
        assert checker.result.status == CheckStatus.IDLE
        assert checker.result.has_slots is False

    def test_result_is_accessible(self):
        checker = VFSChecker(headless=True)
        result = checker.result
        assert result.last_check is None
        assert result.slots == []

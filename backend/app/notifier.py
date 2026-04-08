from __future__ import annotations

import logging
import threading

from app.models import SlotInfo, VFS_BOOKING_URL

logger = logging.getLogger(__name__)


def _send_desktop_notification(title: str, message: str) -> None:
    try:
        from plyer import notification

        notification.notify(
            title=title,
            message=message,
            timeout=30,
        )
    except Exception as e:
        logger.warning("Не удалось отправить уведомление: %s", e)


def notify_slots_found(slots: list[SlotInfo]) -> None:
    if not slots:
        return

    cities = set(s.city.value for s in slots)
    title = f"VFS: Найдены слоты! ({', '.join(cities)})"

    lines = [s.display_label for s in slots[:5]]
    if len(slots) > 5:
        lines.append(f"...и ещё {len(slots) - 5}")
    lines.append(f"\n{VFS_BOOKING_URL}")
    message = "\n".join(lines)

    logger.info("УВЕДОМЛЕНИЕ: %s — %s", title, message)

    thread = threading.Thread(
        target=_send_desktop_notification,
        args=(title, message),
        daemon=True,
    )
    thread.start()

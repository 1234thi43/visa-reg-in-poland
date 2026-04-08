"""
Запуск VFS Visa Slot Monitor.

Запускает FastAPI-сервер + Playwright-браузер для мониторинга.
Откройте http://localhost:8000 в браузере для дашборда.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent


def ensure_playwright_browsers():
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            p.chromium.executable_path
    except Exception:
        print("Устанавливаю браузеры Playwright...")
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])


def main():
    ensure_playwright_browsers()

    import uvicorn

    sys.path.insert(0, str(ROOT / "backend"))
    from app.main import create_app

    app = create_app(start_checker=True)

    print("\n" + "=" * 60)
    print("  VFS Poland — Мониторинг слотов")
    print("  Дашборд: http://localhost:8000")
    print("  Проверка каждые 60 секунд")
    print("=" * 60 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()

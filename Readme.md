Как запустить^

# 1. Установить зависимости (если ещё не установлены)
cd backend && pip install -r requirements.txt
python -m playwright install chromium

# 2. Собрать фронтенд (уже собран)
cd frontend && npm install && npm run build

# 3. Запустить всё
python start.py

Порт http://localhost:8000/
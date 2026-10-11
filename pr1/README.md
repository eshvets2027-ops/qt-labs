# Практична робота №1 — Інтеграція зовнішнього REST API

Вебзастосунок на FastAPI шукає місто через Open-Meteo Geocoding API, отримує координати та запитує поточну температуру і швидкість вітру через Forecast API.

## Запуск на macOS

1. Відкрийте Terminal і перейдіть у папку `pr1`.
2. Створіть віртуальне середовище та активуйте його:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Встановіть залежності:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Перевірте доступ до Open-Meteo:

   ```bash
   python check_env.py
   ```

5. Запустіть вебзастосунок:

   ```bash
   uvicorn app.main:app --reload
   ```

6. Відкрийте `http://127.0.0.1:8000` у браузері.

## JSON API

Приклад: `http://127.0.0.1:8000/api/weather?city=Kyiv`

- Успіх: JSON з містом, температурою та швидкістю вітру.
- Порожня назва: HTTP 400.
- Місто не знайдено: HTTP 404.
- Помилка зовнішнього API: HTTP 502.

## Обробка помилок

- HTTP параметри передаються через `requests.get(..., params=...)`.
- Кожен запит має таймаут 10 секунд.
- Окремо обробляються таймаут, помилка з'єднання, HTTP 4xx/5xx, невалідний JSON і відсутні поля.
- Інтеграція з Open-Meteo винесена в `app/weather_api.py`; веб-рівень знаходиться в `app/main.py`.
- `samples/` містить приклади структури відповідей для вивчення JSON.

## Git

З кореня репозиторію можна зберегти роботу командами:

```bash
git add pr1
git commit -m "Add practical work 1 weather REST API"
git push
```

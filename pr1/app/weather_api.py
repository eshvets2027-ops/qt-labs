"""Open-Meteo integration module: HTTP details stay in this file."""
import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT_SECONDS = 10


class WeatherAPIError(Exception):
    """A readable error from the weather integration layer."""


def _get_json(url: str, params: dict) -> dict:
    try:
        response = requests.get(url, params=params, timeout=TIMEOUT_SECONDS)
        if 400 <= response.status_code < 500:
            raise WeatherAPIError(
                f"Сервіс відхилив запит (HTTP {response.status_code}). Перевірте назву міста."
            )
        if response.status_code >= 500:
            raise WeatherAPIError(
                f"Зовнішній сервіс тимчасово недоступний (HTTP {response.status_code}). Спробуйте пізніше."
            )
        response.raise_for_status()
    except requests.Timeout as exc:
        raise WeatherAPIError("Зовнішній сервіс не відповів вчасно. Спробуйте ще раз.") from exc
    except requests.ConnectionError as exc:
        raise WeatherAPIError("Не вдалося з'єднатися із сервісом погоди. Перевірте інтернет.") from exc
    except requests.RequestException as exc:
        raise WeatherAPIError("Під час запиту до сервісу погоди сталася мережева помилка.") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise WeatherAPIError("Сервіс повернув відповідь у невідомому форматі.") from exc

    if not isinstance(data, dict):
        raise WeatherAPIError("Сервіс повернув неочікуваний формат даних.")
    return data


def get_current_weather(city: str) -> dict:
    """Find city coordinates, then fetch current temperature and wind speed."""
    city = city.strip()
    if not city:
        raise ValueError("Введіть назву міста.")

    geo_data = _get_json(
        GEOCODING_URL,
        {"name": city, "count": 1, "language": "uk", "format": "json"},
    )
    results = geo_data.get("results")
    if not isinstance(results, list) or not results:
        raise LookupError(f"Місто «{city}» не знайдено. Перевірте назву та спробуйте ще раз.")

    place = results[0]
    try:
        latitude = float(place["latitude"])
        longitude = float(place["longitude"])
        place_name = str(place["name"])
        country = str(place.get("country", ""))
    except (KeyError, TypeError, ValueError) as exc:
        raise WeatherAPIError("Сервіс геокодування повернув неповні дані.") from exc

    forecast_data = _get_json(
        FORECAST_URL,
        {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,wind_speed_10m",
            "timezone": "auto",
        },
    )

    current = forecast_data.get("current")
    if not isinstance(current, dict):
        raise WeatherAPIError("У відповіді сервісу немає даних про поточну погоду.")

    try:
        temperature = float(current["temperature_2m"])
        wind_speed = float(current["wind_speed_10m"])
        time = str(current.get("time", ""))
        units = forecast_data.get("current_units", {})
        temperature_unit = str(units.get("temperature_2m", "°C")) if isinstance(units, dict) else "°C"
        wind_unit = str(units.get("wind_speed_10m", "km/h")) if isinstance(units, dict) else "km/h"
    except (KeyError, TypeError, ValueError) as exc:
        raise WeatherAPIError("Дані про температуру або вітер мають неочікуваний формат.") from exc

    return {
        "city": place_name,
        "country": country,
        "temperature": temperature,
        "temperature_unit": temperature_unit,
        "wind_speed": wind_speed,
        "wind_unit": wind_unit,
        "time": time,
    }

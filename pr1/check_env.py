"""Basic environment and Open-Meteo connectivity check."""
import requests

URL = "https://geocoding-api.open-meteo.com/v1/search"

def main():
    try:
        response = requests.get(
            URL,
            params={"name": "Kyiv", "count": 1, "language": "uk", "format": "json"},
            timeout=10,
        )
        print("HTTP status:", response.status_code)
        response.raise_for_status()
        data = response.json()
        print("JSON received:", isinstance(data, dict))
        print("Kyiv result found:", bool(data.get("results")))
    except requests.Timeout:
        print("Timeout: Open-Meteo did not respond within 10 seconds.")
    except requests.RequestException as exc:
        print("Network/API error:", exc)
    except ValueError:
        print("The service returned invalid JSON.")

if __name__ == "__main__":
    main()

from __future__ import annotations

from typing import Any

import requests

OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


def fetch_weather(latitude: float, longitude: float, api_key: str | None) -> dict[str, Any] | None:
    if not api_key:
        return None

    response = requests.get(
        OPENWEATHER_URL,
        params={
            "lat": latitude,
            "lon": longitude,
            "appid": api_key,
            "units": "metric",
        },
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()
    rain = payload.get("rain") or {}
    weather = (payload.get("weather") or [{}])[0]
    return {
        "temperature_c": (payload.get("main") or {}).get("temp"),
        "humidity": (payload.get("main") or {}).get("humidity"),
        "precip_mm": rain.get("1h", rain.get("3h")),
        "condition": weather.get("description"),
    }

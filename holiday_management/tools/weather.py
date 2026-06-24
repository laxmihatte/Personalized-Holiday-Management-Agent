"""A weather tool the Researcher agent can call to ground itineraries in real
forecasts. Uses the free, no-key Open-Meteo API (geocoding + daily forecast).

The function is registered with AutoGen as a tool; its name, type hints and
docstring become the schema the model sees, so keep the docstring descriptive.
All failures are caught and returned as readable text so a network hiccup never
crashes the agent run.
"""
import httpx

from holiday_management.utils.logging_config import get_app_logger

logger = get_app_logger("weather_tool")

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


async def get_weather_forecast(city: str, days: int = 5) -> str:
    """Get the daily weather forecast for a city to inform trip planning.

    Args:
        city: The destination city, e.g. "Paris" or "Tokyo".
        days: Number of days to forecast (1-16).

    Returns:
        A human-readable, day-by-day forecast summary (highs/lows in °C and
        chance of rain), or an explanatory message if the city or forecast
        could not be retrieved.
    """
    days = max(1, min(days, 16))
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            geo = await client.get(
                GEOCODE_URL, params={"name": city, "count": 1}
            )
            geo.raise_for_status()
            results = geo.json().get("results")
            if not results:
                logger.info("No geocoding match for city %r", city)
                return f"Could not find a location named '{city}'."

            place = results[0]
            lat, lon = place["latitude"], place["longitude"]
            label = ", ".join(
                p for p in (place.get("name"), place.get("country")) if p
            )

            forecast = await client.get(
                FORECAST_URL,
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                    "forecast_days": days,
                    "timezone": "auto",
                },
            )
            forecast.raise_for_status()
            daily = forecast.json().get("daily", {})
    except Exception as exc:  # noqa: BLE001 - tool must degrade, not crash
        logger.warning("Weather lookup failed for %r: %s", city, exc)
        return f"Weather data for '{city}' is currently unavailable."

    return _format_forecast(label or city, daily)


def _format_forecast(label: str, daily: dict) -> str:
    dates = daily.get("time", [])
    highs = daily.get("temperature_2m_max", [])
    lows = daily.get("temperature_2m_min", [])
    rain = daily.get("precipitation_probability_max", [])
    if not dates:
        return f"No forecast data returned for {label}."

    lines = [f"Weather forecast for {label}:"]
    for i, date in enumerate(dates):
        high = highs[i] if i < len(highs) else "?"
        low = lows[i] if i < len(lows) else "?"
        pop = rain[i] if i < len(rain) else None
        rain_note = f", {pop}% chance of rain" if pop is not None else ""
        lines.append(f"- {date}: {low}–{high}°C{rain_note}")
    return "\n".join(lines)

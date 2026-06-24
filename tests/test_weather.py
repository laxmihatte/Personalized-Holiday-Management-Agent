import httpx
import pytest

from holiday_management.tools import weather


def _mock_transport(handler):
    """Build an AsyncClient whose requests are served by `handler`."""
    return httpx.MockTransport(handler)


@pytest.fixture
def patch_client(monkeypatch):
    def install(handler):
        real_async_client = httpx.AsyncClient

        def factory(*args, **kwargs):
            kwargs["transport"] = _mock_transport(handler)
            return real_async_client(*args, **kwargs)

        monkeypatch.setattr(weather.httpx, "AsyncClient", factory)

    return install


@pytest.mark.asyncio
async def test_forecast_formats_days(patch_client):
    def handler(request: httpx.Request) -> httpx.Response:
        if "geocoding" in request.url.host:
            return httpx.Response(
                200,
                json={"results": [{"latitude": 48.85, "longitude": 2.35,
                                   "name": "Paris", "country": "France"}]},
            )
        return httpx.Response(
            200,
            json={"daily": {
                "time": ["2026-07-01", "2026-07-02"],
                "temperature_2m_max": [28, 22],
                "temperature_2m_min": [18, 15],
                "precipitation_probability_max": [10, 80],
            }},
        )

    patch_client(handler)
    out = await weather.get_weather_forecast("Paris", days=2)
    assert "Paris, France" in out
    assert "2026-07-01: 18–28°C, 10% chance of rain" in out
    assert "80% chance of rain" in out


@pytest.mark.asyncio
async def test_unknown_city(patch_client):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"results": []})

    patch_client(handler)
    out = await weather.get_weather_forecast("Nowheresville")
    assert "Could not find" in out


@pytest.mark.asyncio
async def test_network_error_degrades(patch_client):
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom")

    patch_client(handler)
    out = await weather.get_weather_forecast("Paris")
    assert "unavailable" in out


def test_days_clamped():
    # pure helper check: formatting tolerates missing fields
    out = weather._format_forecast("Paris", {"time": ["2026-07-01"],
                                             "temperature_2m_max": [30]})
    assert "2026-07-01" in out

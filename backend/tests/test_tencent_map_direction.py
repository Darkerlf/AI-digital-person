from app.services.tencent_map_client import TencentMapClient


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self.payload


class FakeHttpClient:
    last_url = ""
    last_params: dict | None = None

    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def get(self, url: str, params: dict):
        FakeHttpClient.last_url = url
        FakeHttpClient.last_params = params
        return FakeResponse(self.payload)


def test_direction_walking_returns_normalized_route(monkeypatch):
    payload = {
        "status": 0,
        "result": {
            "routes": [
                {
                    "distance": 180,
                    "duration": 4,
                    "polyline": [31.0, 120.0, 1000, 1000],
                }
            ]
        },
    }

    monkeypatch.setattr(
        "app.services.tencent_map_client.httpx.Client",
        lambda timeout: FakeHttpClient(payload),
    )

    result = TencentMapClient(api_key="test-key").direction_walking(
        from_point={"latitude": 31.0, "longitude": 120.0},
        to_point={"latitude": 31.001, "longitude": 120.001},
    )

    assert FakeHttpClient.last_url.endswith("/ws/direction/v1/walking/")
    assert FakeHttpClient.last_params == {
        "from": "31.0,120.0",
        "to": "31.001,120.001",
        "key": "test-key",
    }
    assert result == {
        "distance_meters": 180,
        "duration_minutes": 4,
        "polyline": [
            {"latitude": 31.0, "longitude": 120.0},
            {"latitude": 31.001, "longitude": 120.001},
        ],
        "provider": "tencent_walking",
        "raw": payload["result"]["routes"][0],
    }


def test_direction_walking_returns_none_without_available_route(monkeypatch):
    monkeypatch.setattr(
        "app.services.tencent_map_client.httpx.Client",
        lambda timeout: FakeHttpClient({"status": 1, "message": "quota exceeded"}),
    )

    result = TencentMapClient(api_key="test-key").direction_walking(
        from_point={"latitude": 31.0, "longitude": 120.0},
        to_point={"latitude": 31.001, "longitude": 120.001},
    )

    assert result is None

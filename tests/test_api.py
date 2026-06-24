import pytest
from fastapi.testclient import TestClient

import app as app_module
from app import app


@pytest.fixture
def client(monkeypatch):
    """A TestClient with the agent team and memory mocked out, so no LLM
    calls or vector store are needed."""

    class FakeMessage:
        def __init__(self, source, content):
            self.source = source
            self.content = content

    class FakeResult:
        messages = [
            FakeMessage("User", "Plan a trip to Rome"),
            FakeMessage("Holiday_Planner", "Day 1: Colosseum. Day 2: Vatican."),
            FakeMessage("Holiday_Researcher", "Colosseum opens 9am. stop"),
        ]

    class FakeTeam:
        async def run(self, task=None):
            return FakeResult()

    monkeypatch.setattr(app_module, "build_team", lambda: FakeTeam())
    monkeypatch.setattr(app_module, "recall_preferences", lambda uid, q: [])
    monkeypatch.setattr(app_module, "remember_preferences", lambda uid, c: None)
    return TestClient(app)


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_plan_success(client):
    res = client.post("/plan", json={"content": "Plan a 5-day trip to Rome"})
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "success"
    assert body["user_id"] == "guest"
    assert body["message_count"] == 3
    assert body["messages"][1]["source"] == "Holiday_Planner"
    assert body["signature"]


def test_plan_rejects_short_content(client):
    res = client.post("/plan", json={"content": "hi"})
    assert res.status_code == 422


def test_plan_uses_recalled_preferences(monkeypatch, client):
    captured = {}

    class FakeResult:
        messages = []

    class FakeTeam:
        async def run(self, task=None):
            captured["content"] = task.content
            return FakeResult()

    monkeypatch.setattr(app_module, "build_team", lambda: FakeTeam())
    monkeypatch.setattr(
        app_module, "recall_preferences", lambda uid, q: ["prefers boutique hotels"]
    )

    res = client.post(
        "/plan", json={"content": "Plan a trip to Rome", "user_id": "laxmi"}
    )
    assert res.status_code == 200
    # the recalled preference was injected into the task sent to the agents
    assert "boutique hotels" in captured["content"]


def test_plan_handles_team_failure(monkeypatch, client):
    class FakeTeam:
        async def run(self, task=None):
            raise RuntimeError("model exploded")

    monkeypatch.setattr(app_module, "build_team", lambda: FakeTeam())
    res = client.post("/plan", json={"content": "Plan a trip to Rome"})
    assert res.status_code == 500

import pytest
from pydantic import ValidationError

from holiday_management.models.schemas import PlanRequest, PlanResponse, AgentMessage


def test_plan_request_defaults():
    req = PlanRequest(content="Plan a 5-day trip to Rome")
    assert req.user_id == "guest"
    assert req.source == "User"
    assert req.tags == []


def test_plan_request_strips_content():
    req = PlanRequest(content="   Plan a trip to Rome   ")
    assert req.content == "Plan a trip to Rome"


def test_plan_request_rejects_short_content():
    with pytest.raises(ValidationError):
        PlanRequest(content="hi")


def test_plan_request_rejects_blank_content():
    with pytest.raises(ValidationError):
        PlanRequest(content="          ")


def test_plan_response_serialises():
    resp = PlanResponse(
        user_id="guest",
        signature="plan_trip_rome",
        message_count=1,
        messages=[AgentMessage(source="Holiday_Planner", content="Day 1: ...")],
        remembered=["likes museums"],
    )
    dumped = resp.model_dump()
    assert dumped["status"] == "success"
    assert dumped["messages"][0]["source"] == "Holiday_Planner"
    assert "processed_at" in dumped

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from autogen_agentchat.messages import TextMessage

from holiday_management.teams.holiday_team import build_team
from holiday_management.models.schemas import PlanRequest, PlanResponse, AgentMessage
from holiday_management.utils.query_processing import handle_query
from holiday_management.utils.logging_config import get_app_logger
from holiday_management.memory.holiday_memory import recall_preferences, remember_preferences

logger = get_app_logger("holiday_api")

app = FastAPI(title="Holiday Management API")

# serve static files from ./static
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/plan", response_model=PlanResponse)
async def plan(req: PlanRequest):
    logger.info("Plan request from user %s", req.user_id)

    # 1. Validate & normalise the trip description.
    try:
        processed = handle_query(req.content)
    except ValueError as exc:
        logger.warning("Invalid trip request from %s: %s", req.user_id, exc)
        raise HTTPException(status_code=422, detail=str(exc))
    logger.debug("Trip signature: %s", processed["signature"])

    # 2. Recall this traveller's past preferences and fold them into the task.
    remembered = recall_preferences(req.user_id, req.content)
    content = req.content
    if remembered:
        prefs = "\n".join(f"- {p}" for p in remembered)
        content = (
            f"{req.content}\n\n"
            f"Known traveller preferences (personalise the plan around these):\n{prefs}"
        )

    # 3. Run the planner/researcher team.
    try:
        task = TextMessage(content=content, source=req.source)
        result = await build_team().run(task=task)
    except Exception as exc:
        logger.exception("Planning failed for user %s", req.user_id)
        raise HTTPException(status_code=500, detail=str(exc))

    messages = [AgentMessage(source=m.source, content=m.content) for m in result.messages]

    # 4. Remember this request for next time.
    remember_preferences(req.user_id, req.content)

    logger.info("Returning %d message(s) for user %s", len(messages), req.user_id)
    return PlanResponse(
        user_id=req.user_id,
        signature=processed["signature"],
        message_count=len(messages),
        messages=messages,
        remembered=remembered,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

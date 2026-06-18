from autogen_agentchat.agents import AssistantAgent
from holiday_management.models.gpt_model import model_client

planner_agent = AssistantAgent(
    name="Holiday_Planner",
    description="A Holiday planner agent that helps users plan their trips.",
    model_client=model_client,
    system_message=(
        "You are a Holiday Planner agent. You build the day-by-day itinerary: "
        "structure the trip into days, suggest the order of attractions, and handle "
        "timing and logistics. Do NOT repeat the researcher's work — focus only on "
        "the schedule and structure. Wait for the researcher to add details, then "
        "refine the plan based on their input."
    )
)
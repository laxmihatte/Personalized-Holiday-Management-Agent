from autogen_agentchat.agents import AssistantAgent
from holiday_management.models.gpt_model import model_client

researcher_agent = AssistantAgent(
    name="Holiday_Researcher",
    description="A Holiday researcher agent that helps users research their holiday destinations.",
    model_client=model_client,
    system_message=(
        "You are a Holiday Researcher agent. You add concrete detail to the planner's "
        "itinerary: specific attractions, opening hours, local customs, food recommendations, "
        "and practical tips. Do NOT rewrite the whole itinerary — only enrich it with "
        "researched information. When you believe the plan is complete and the user has "
        "enough information, end your message with the word 'stop'."
    )
)
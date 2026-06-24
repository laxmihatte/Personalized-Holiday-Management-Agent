from autogen_agentchat.agents import AssistantAgent
from holiday_management.models.gpt_model import model_client
from holiday_management.tools.weather import get_weather_forecast

researcher_agent = AssistantAgent(
    name="Holiday_Researcher",
    description="A Holiday researcher agent that helps users research their holiday destinations.",
    model_client=model_client,
    tools=[get_weather_forecast],
    reflect_on_tool_use=True,
    system_message=(
        "You are a Holiday Researcher agent. You add concrete detail to the planner's "
        "itinerary: specific attractions, opening hours, local customs, food recommendations, "
        "and practical tips. "
        "Always call the get_weather_forecast tool for the destination before giving advice, "
        "and use the forecast to tailor the plan — prefer indoor activities (museums, galleries) "
        "on days with a high chance of rain and outdoor activities on clear days. "
        "Do NOT rewrite the whole itinerary — only enrich it with researched information. "
        "When you believe the plan is complete and the user has enough information, end your "
        "message with the word 'stop'."
    )
)

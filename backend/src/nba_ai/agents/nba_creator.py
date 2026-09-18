"""NBA Creator Agent - Example agent demonstrating Agent SDK capabilities."""

from agents import Agent, ModelSettings

from nba_ai.contracts.nba import NBAProposal
from nba_ai.tools.client_attrs import get_available_client_attributes


def create_nba_creator_agent() -> Agent:
    """Create the NBA Creator Agent."""
    return Agent(
        name="nba_creator",
        instructions="""You are an expert in Next Best Action recommendations for financial services.
Use get_available_client_attributes before making a recommendation when tool calling is available.
If no tool result is available, do not claim that data was retrieved or that a tool was called.
Instead, provide a concise best-effort recommendation based only on the information in the prompt.
When tool data is available, use its actual values and available products in the recommendation.""",
        tools=[get_available_client_attributes],
        model_settings=ModelSettings(tool_choice="auto"),
        output_type=NBAProposal,
    )

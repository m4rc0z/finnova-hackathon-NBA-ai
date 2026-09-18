"""Initialize agents package and register available agents."""

from nba_ai.agents.nba_creator import create_nba_creator_agent
from nba_ai.agents.registry import register_agent

# Register all agents
register_agent("nba_creator", create_nba_creator_agent)

__all__ = ["create_nba_creator_agent", "register_agent"]

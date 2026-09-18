"""Orchestration boundary for registered agents."""

import logging
from typing import Any

from nba_ai.agents.registry import list_agents
from nba_ai.config import Settings
from nba_ai.services.agent_runtime import AgentRunError, run_agent

logger = logging.getLogger(__name__)


def list_available_agents() -> list[str]:
    """Return the names of agents available to the orchestrator."""
    return list_agents()


def run_orchestrated_agent(
    agent_name: str,
    input_text: str,
    settings: Settings,
    context: dict[str, Any] | None = None,
) -> Any:
    """Validate and delegate a run to a registered agent."""
    if agent_name not in list_agents():
        msg = f"Agent '{agent_name}' is not available to the orchestrator"
        logger.warning(msg)
        raise AgentRunError(msg)

    logger.info("Orchestrating agent '%s'", agent_name)
    return run_agent(
        agent_name=agent_name,
        input_text=input_text,
        settings=settings,
        context=context,
    )

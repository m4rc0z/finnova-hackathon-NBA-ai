"""Agent Runtime Service - Boundary layer for agent execution."""

import json
import logging
from typing import Any

from agents import OpenAIProvider, RunConfig, set_tracing_disabled
from agents.run import AgentRunner

from nba_ai.agents.registry import get_agent
from nba_ai.config import Settings
from nba_ai.tools.client_attrs import get_available_client_attributes_data

logger = logging.getLogger(__name__)

# Swisscom is the model provider; OpenAI trace export would require a separate
# OPENAI_API_KEY and is not applicable to this endpoint.
set_tracing_disabled(True)


class AgentRunError(Exception):
    """Raised when an agent run fails."""

    pass


def run_agent(
    agent_name: str,
    input_text: str,
    settings: Settings,
    context: dict[str, Any] | None = None,
) -> Any:
    """
    Execute a named agent with the given input (synchronously).

    This is the primary boundary layer between HTTP handlers and the agent runtime.
    Later, OpenClaw/MCP adapters will call this interface to orchestrate agents.

    Args:
        agent_name: Name of the agent to run (must be registered)
        input_text: Input text/prompt for the agent
        settings: Application configuration (includes Swisscom endpoint settings)
        context: Optional context dict for the agent

    Returns:
        The agent's structured output (as defined by agent's output_type)

    Raises:
        AgentRunError: If the agent fails or is not found
    """
    try:
        # Get the agent factory from registry
        agent_factory = get_agent(agent_name)
        agent = agent_factory()

        # Swisscom exposes an OpenAI-compatible Chat Completions endpoint.
        provider = OpenAIProvider(
            api_key=settings.swisscom_api_key,
            base_url=settings.swisscom_base_url,
            use_responses=False,
        )
        run_config = RunConfig(
            model=settings.swisscom_model,
            model_provider=provider,
        )

        # Create runner and execute synchronously
        runner = AgentRunner()
        agent_input = input_text
        if agent_name == "nba_creator":
            capability_data = json.dumps(
                get_available_client_attributes_data(),
                ensure_ascii=True,
                sort_keys=True,
            )
            agent_input = (
                f"{input_text}\n\n"
                "Deterministic capability data supplied by the runtime fallback. "
                "Use these actual values in your recommendation; do not claim that "
                "the data is unavailable:\n"
                f"{capability_data}"
            )
        result = runner.run_sync(
            starting_agent=agent,
            input=agent_input,
            run_config=run_config,
        )

        logger.info(
            f"Agent '{agent_name}' run completed",
            extra={"agent": agent_name},
        )

        # The SDK validates structured output and exposes it as final_output.
        return result.final_output

    except KeyError as e:
        msg = f"Agent '{agent_name}' not found in registry"
        logger.error(msg)
        raise AgentRunError(msg) from e
    except Exception as e:
        msg = f"Agent '{agent_name}' execution failed: {str(e)}"
        logger.error(msg, exc_info=True)
        raise AgentRunError(msg) from e

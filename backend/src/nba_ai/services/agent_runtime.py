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

set_tracing_disabled(True)


class AgentRunError(Exception):
    """Raised when an agent run fails."""


def run_agent(
    agent_name: str,
    input_text: str,
    settings: Settings,
    context: dict[str, Any] | None = None,
) -> Any:
    """Execute a named agent synchronously."""
    try:
        agent_factory = get_agent(agent_name)
        agent = agent_factory()

        provider = OpenAIProvider(
            api_key=settings.swisscom_api_key,
            base_url=settings.swisscom_base_url,
            use_responses=False,
        )
        run_config = RunConfig(
            model=settings.swisscom_model,
            model_provider=provider,
        )

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

        result = AgentRunner().run_sync(
            starting_agent=agent,
            input=agent_input,
            run_config=run_config,
        )
        logger.info("Agent '%s' run completed", agent_name)
        return result.final_output

    except KeyError as exc:
        msg = f"Agent '{agent_name}' not found in registry"
        logger.error(msg)
        raise AgentRunError(msg) from exc
    except Exception as exc:
        msg = f"Agent '{agent_name}' execution failed: {exc}"
        logger.error(msg, exc_info=True)
        raise AgentRunError(msg) from exc

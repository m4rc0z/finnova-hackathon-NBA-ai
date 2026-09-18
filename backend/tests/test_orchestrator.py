"""Tests for the registered-agent orchestrator."""

from unittest.mock import patch

import pytest

from nba_ai.config import Settings
from nba_ai.contracts.nba import NBAProposal
from nba_ai.services.agent_orchestrator import (
    list_available_agents,
    run_orchestrated_agent,
)
from nba_ai.services.agent_runtime import AgentRunError


def test_list_available_agents():
    """The orchestrator exposes registered agents."""
    assert "nba_creator" in list_available_agents()


@patch("nba_ai.services.agent_orchestrator.run_agent")
def test_run_orchestrated_agent_delegates(mock_run_agent):
    """A registered agent is delegated to the runtime boundary."""
    expected = NBAProposal(name="Test", objective="Goal", explanation="Reason")
    mock_run_agent.return_value = expected
    settings = Settings(swisscom_api_key="test-key")

    result = run_orchestrated_agent(
        agent_name="nba_creator",
        input_text="Test input",
        settings=settings,
    )

    assert result == expected
    mock_run_agent.assert_called_once_with(
        agent_name="nba_creator",
        input_text="Test input",
        settings=settings,
        context=None,
    )


def test_run_orchestrated_agent_rejects_unknown_agent():
    """Unknown agents fail before runtime execution."""
    settings = Settings(swisscom_api_key="test-key")

    with pytest.raises(AgentRunError, match="not available"):
        run_orchestrated_agent(
            agent_name="unknown",
            input_text="Test input",
            settings=settings,
        )

"""Tests for Agent Runtime Service."""

from unittest.mock import MagicMock, patch

import pytest

from nba_ai.config import Settings
from nba_ai.contracts.nba import NBAProposal
from nba_ai.services.agent_runtime import AgentRunError, run_agent


@patch("nba_ai.services.agent_runtime.get_agent")
@patch("nba_ai.services.agent_runtime.AgentRunner")
def test_run_agent_success(mock_runner_class, mock_get_agent):
    """Test successful agent execution."""
    # Create mock agent and runner
    mock_agent = MagicMock()
    mock_agent_factory = MagicMock(return_value=mock_agent)
    mock_get_agent.return_value = mock_agent_factory

    # Create mock result
    mock_result = MagicMock()
    expected_output = NBAProposal(
        name="Test NBA",
        objective="Test Obj",
        explanation="Test Exp",
    )
    mock_result.final_output = expected_output
    mock_result.status = "ok"

    mock_runner = MagicMock()
    mock_runner.run_sync.return_value = mock_result
    mock_runner_class.return_value = mock_runner

    settings = Settings(
        swisscom_api_key="test_key",
        swisscom_base_url="https://example.invalid/v1",
        swisscom_model="test-model",
    )

    result = run_agent(
        agent_name="nba_creator",
        input_text="Test input",
        settings=settings,
    )

    assert result == expected_output
    mock_get_agent.assert_called_once_with("nba_creator")
    mock_agent_factory.assert_called_once()
    mock_runner.run_sync.assert_called_once()
    assert "client_123" in mock_runner.run_sync.call_args.kwargs["input"]
    run_config = mock_runner.run_sync.call_args.kwargs["run_config"]
    assert run_config.model == "test-model"


@patch("nba_ai.services.agent_runtime.get_agent")
def test_run_agent_not_found(mock_get_agent):
    """Test that running a nonexistent agent raises AgentRunError."""
    mock_get_agent.side_effect = KeyError("nba_creator")

    settings = Settings(swisscom_api_key="test_key")

    with pytest.raises(AgentRunError, match="not found"):
        run_agent(
            agent_name="nba_creator",
            input_text="Test",
            settings=settings,
        )


@patch("nba_ai.services.agent_runtime.get_agent")
@patch("nba_ai.services.agent_runtime.AgentRunner")
def test_run_agent_execution_error(mock_runner_class, mock_get_agent):
    """Test that agent execution errors are wrapped in AgentRunError."""
    mock_agent = MagicMock()
    mock_agent_factory = MagicMock(return_value=mock_agent)
    mock_get_agent.return_value = mock_agent_factory

    mock_runner = MagicMock()
    mock_runner.run_sync.side_effect = RuntimeError("Mock LLM failure")
    mock_runner_class.return_value = mock_runner

    settings = Settings(swisscom_api_key="test_key")

    with pytest.raises(AgentRunError, match="execution failed"):
        run_agent(
            agent_name="nba_creator",
            input_text="Test",
            settings=settings,
        )

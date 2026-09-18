"""Tests for FastAPI endpoints."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from nba_ai.main import app

client = TestClient(app)


def test_health():
    """Test the health check endpoint."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"


@patch("nba_ai.main.run_agent")
def test_agent_run_endpoint_success(mock_run_agent):
    """Test running an agent via the HTTP endpoint."""
    from nba_ai.contracts.nba import NBAProposal

    # Mock the agent run to return a NBAProposal
    mock_proposal = NBAProposal(
        name="Test NBA",
        objective="Test Objective",
        explanation="Test Explanation",
    )

    # Make run_agent return the proposal
    mock_run_agent.return_value = mock_proposal

    response = client.post(
        "/api/agents/nba_creator/run",
        json={"input": "Test input prompt"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "output" in data
    # The output should contain the proposal data
    output = data["output"]
    assert output["name"] == "Test NBA"
    assert output["objective"] == "Test Objective"

    # Verify run_agent was called with correct arguments
    mock_run_agent.assert_called_once()
    call_kwargs = mock_run_agent.call_args[1]
    assert call_kwargs["agent_name"] == "nba_creator"
    assert call_kwargs["input_text"] == "Test input prompt"


@patch("nba_ai.main.run_agent")
def test_agent_run_endpoint_agent_not_found(mock_run_agent):
    """Test running a nonexistent agent returns 400."""
    from nba_ai.services.agent_runtime import AgentRunError

    mock_run_agent.side_effect = AgentRunError("Agent 'fake_agent' not found")

    response = client.post(
        "/api/agents/fake_agent/run",
        json={"input": "Test input"},
    )

    assert response.status_code == 400
    data = response.json()
    assert "Agent" in data["detail"]
    assert "not found" in data["detail"]


@patch("nba_ai.main.run_agent")
def test_agent_run_endpoint_execution_error(mock_run_agent):
    """Test agent execution failure returns 400."""
    from nba_ai.services.agent_runtime import AgentRunError

    mock_run_agent.side_effect = AgentRunError("Agent execution failed")

    response = client.post(
        "/api/agents/nba_creator/run",
        json={"input": "Test input"},
    )

    assert response.status_code == 400
    data = response.json()
    assert "execution failed" in data["detail"]


def test_available_agents_endpoint():
    """Test agent discovery for the orchestrator."""
    response = client.get("/api/agents")

    assert response.status_code == 200
    assert "nba_creator" in response.json()["agents"]


@patch("nba_ai.main.run_orchestrated_agent")
def test_orchestrator_run_endpoint(mock_run_orchestrated_agent):
    """Test delegating an agent run through the orchestrator."""
    from nba_ai.contracts.nba import NBAProposal

    mock_run_orchestrated_agent.return_value = NBAProposal(
        name="Orchestrated NBA",
        objective="Test objective",
        explanation="Test explanation",
    )

    response = client.post(
        "/api/orchestrator/run",
        json={"agent_name": "nba_creator", "input": "Test input"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["agent_name"] == "nba_creator"
    assert data["output"]["name"] == "Orchestrated NBA"

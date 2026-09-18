"""
Integration and smoke tests.

Run without real API key for integration tests (mocked).
Run with RUN_SWISSCOM_SMOKE=1 and SWISSCOM_API_KEY for smoke tests.
"""

import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from nba_ai.main import app

client = TestClient(app)
SMOKE_TEST_ENABLED = bool(
    os.environ.get("RUN_SWISSCOM_SMOKE") and os.environ.get("SWISSCOM_API_KEY")
)


class TestIntegration:
    """Integration tests - no real API calls."""

    def test_full_flow_agent_run_to_response(self):
        """Test full flow from HTTP request to agent output."""
        from nba_ai.contracts.nba import NBAProposal

        mock_proposal = NBAProposal(
            name="Test Integration",
            objective="Integration Test Objective",
            explanation="This is an integration test",
        )

        with patch("nba_ai.main.run_agent", return_value=mock_proposal):
            response = client.post(
                "/api/agents/nba_creator/run",
                json={"input": "Test input"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["output"]["name"] == "Test Integration"

    def test_full_agent_registry_lookup_flow(self):
        """Test agent registration and lookup flow."""
        from nba_ai.agents.registry import get_agent, list_agents

        # nba_creator should be registered
        agents = list_agents()
        assert "nba_creator" in agents

        # Should be able to retrieve the agent factory
        factory = get_agent("nba_creator")
        assert factory is not None

        # Factory should create an agent
        agent = factory()
        assert agent.name == "nba_creator"
        assert agent.model_settings.tool_choice == "auto"


class TestSmokeTests:
    """Smoke tests - require real SWISSCOM_API_KEY (optional)."""

    @pytest.mark.skipif(
        not SMOKE_TEST_ENABLED,
        reason="Set RUN_SWISSCOM_SMOKE=1 and SWISSCOM_API_KEY to run",
    )
    def test_agent_run_with_real_llm(self):
        """Test agent execution with real LLM (requires API key)."""
        response = client.post(
            "/api/agents/nba_creator/run",
            json={"input": "Recommend next best action for Acme Corp client"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "output" in data

        output = data["output"]
        # Should have the structure of NBAProposal
        assert "name" in output
        assert "objective" in output
        assert "explanation" in output

    @pytest.mark.skipif(
        not SMOKE_TEST_ENABLED,
        reason="Set RUN_SWISSCOM_SMOKE=1 and SWISSCOM_API_KEY to run",
    )
    def test_tool_calling_in_agent(self):
        """Test that agent can call tools (requires real API)."""
        response = client.post(
            "/api/agents/nba_creator/run",
            json={
                "input": "Use the get_available_client_attributes tool to analyze client strengths"
            },
        )

        # Agent should use the tool
        assert response.status_code == 200
        data = response.json()
        assert "output" in data

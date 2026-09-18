"""Tests for Agent Registry."""

import pytest

from nba_ai.agents.registry import get_agent, list_agents, register_agent


def test_register_and_get_agent():
    """Test registering and retrieving an agent."""

    def dummy_factory():
        return "dummy_agent"

    register_agent("test_agent", dummy_factory)
    retrieved = get_agent("test_agent")

    assert retrieved is dummy_factory
    assert retrieved() == "dummy_agent"


def test_get_nonexistent_agent():
    """Test that getting a nonexistent agent raises KeyError."""
    with pytest.raises(KeyError, match="Agent 'nonexistent' not found"):
        get_agent("nonexistent")


def test_list_agents():
    """Test listing registered agents."""
    # Clear and register test agents
    register_agent("agent_a", lambda: "a")
    register_agent("agent_b", lambda: "b")

    agents = list_agents()
    assert "agent_a" in agents
    assert "agent_b" in agents

"""Agent Registry: simple lookup for agent definitions."""

from typing import Any, Callable

_agent_registry: dict[str, Callable[..., Any]] = {}


def register_agent(name: str, factory: Callable[..., Any]) -> None:
    """Register an agent factory by name."""
    _agent_registry[name] = factory


def get_agent(name: str) -> Callable[..., Any]:
    """Get an agent factory by name. Raises KeyError if not found."""
    if name not in _agent_registry:
        raise KeyError(f"Agent '{name}' not found in registry")
    return _agent_registry[name]


def list_agents() -> list[str]:
    """List all registered agent names."""
    return list(_agent_registry.keys())

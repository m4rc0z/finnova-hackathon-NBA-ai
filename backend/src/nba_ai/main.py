"""FastAPI application for the agent runtime."""

import logging
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

import nba_ai.agents  # noqa: F401
from nba_ai.config import get_settings
from nba_ai.services.agent_orchestrator import (
    list_available_agents,
    run_orchestrated_agent,
)
from nba_ai.services.agent_runtime import AgentRunError, run_agent

logger = logging.getLogger(__name__)


class AgentRunRequest(BaseModel):
    """Request to run an agent."""

    input: str = Field(..., description="Input text/prompt for the agent")


class OrchestratorRunRequest(BaseModel):
    """Request for the registered-agent orchestrator."""

    agent_name: str = Field(..., description="Registered agent to execute")
    input: str = Field(..., description="Input text/prompt for the agent")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    version: str = Field(default="0.1.0", description="Service version")


app = FastAPI(
    title="NBA AI Backend",
    description="Minimal Python Agent Runtime for Next Best Action Studio",
    version="0.1.0",
)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="ok")


@app.get("/api/agents")
async def available_agents() -> dict[str, list[str]]:
    """List agents available to the orchestrator."""
    return {"agents": list_available_agents()}


@app.post("/api/agents/{agent_name}/run")
def run_agent_endpoint(agent_name: str, request: AgentRunRequest) -> Any:
    """Run a named agent with the given input."""
    settings = get_settings()

    try:
        result = run_agent(
            agent_name=agent_name,
            input_text=request.input,
            settings=settings,
        )
        return {"output": result}
    except AgentRunError as exc:
        logger.warning("Agent run failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Unexpected error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@app.post("/api/orchestrator/run")
def orchestrator_run_endpoint(request: OrchestratorRunRequest) -> Any:
    """Run one registered agent through the orchestration boundary."""
    settings = get_settings()

    try:
        result = run_orchestrated_agent(
            agent_name=request.agent_name,
            input_text=request.input,
            settings=settings,
        )
        return {"agent_name": request.agent_name, "output": result}
    except AgentRunError as exc:
        logger.warning("Orchestrator run failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Unexpected orchestrator error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from exc

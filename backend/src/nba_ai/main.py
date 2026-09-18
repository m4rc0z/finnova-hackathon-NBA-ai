"""FastAPI Application - HTTP API for agent runtime."""

import logging
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Import agents to register them
import nba_ai.agents  # noqa: F401
from nba_ai.config import get_settings
from nba_ai.services.agent_runtime import AgentRunError, run_agent

logger = logging.getLogger(__name__)

# Pydantic models for API
class AgentRunRequest(BaseModel):
    """Request to run an agent."""

    input: str = Field(..., description="Input text/prompt for the agent")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    version: str = Field(default="0.1.0", description="Service version")


# Create FastAPI app
app = FastAPI(
    title="NBA AI Backend",
    description="Minimal Python Agent Runtime for Next Best Action Studio",
    version="0.1.0",
)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="ok")


@app.post("/api/agents/{agent_name}/run")
def run_agent_endpoint(agent_name: str, request: AgentRunRequest) -> Any:
    """
    Run a named agent with the given input.

    Args:
        agent_name: Name of the agent (e.g., "nba_creator")
        request: Agent run request with input text

    Returns:
        Agent's structured output

    Raises:
        HTTPException: If agent not found or execution fails
    """
    settings = get_settings()

    try:
        result = run_agent(
            agent_name=agent_name,
            input_text=request.input,
            settings=settings,
        )
        return {"output": result}
    except AgentRunError as e:
        logger.warning(f"Agent run failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e

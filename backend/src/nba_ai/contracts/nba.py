"""NBA response contracts."""

from pydantic import BaseModel, Field


class NBAProposal(BaseModel):
    """Structured output contract for NBA Creator Agent."""

    name: str = Field(..., description="Name or title of the proposal")
    objective: str = Field(..., description="Main objective or goal")
    explanation: str = Field(..., description="Detailed explanation or reasoning")

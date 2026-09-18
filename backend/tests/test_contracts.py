"""Tests for Pydantic Contracts."""

import pytest
from pydantic import ValidationError

from nba_ai.contracts.nba import NBAProposal


def test_nba_proposal_valid():
    """Test creating a valid NBAProposal."""
    proposal = NBAProposal(
        name="Credit Line Expansion",
        objective="Increase available credit",
        explanation="Client has strong credit profile and consistent revenue",
    )

    assert proposal.name == "Credit Line Expansion"
    assert proposal.objective == "Increase available credit"
    assert "strong credit" in proposal.explanation


def test_nba_proposal_missing_fields():
    """Test that missing fields raise validation errors."""
    with pytest.raises(ValidationError):
        NBAProposal(
            name="Test",
            objective="Test objective",
            # missing explanation
        )


def test_nba_proposal_model_dump():
    """Test serializing NBAProposal to dict."""
    proposal = NBAProposal(
        name="Test",
        objective="Test obj",
        explanation="Test exp",
    )

    data = proposal.model_dump()
    assert data == {
        "name": "Test",
        "objective": "Test obj",
        "explanation": "Test exp",
    }

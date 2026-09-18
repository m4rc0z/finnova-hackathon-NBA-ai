from unittest.mock import MagicMock, patch
import pytest

from src.clients.backend_client import BackendClient
from src.services.nba_service import NBAService


@pytest.fixture
def mock_backend_client():
    client = MagicMock(spec=BackendClient)
    client.base_url = "http://mock-backend:8000"
    client.list_collection.return_value = {
        "items": [
            {
                "individual_id": "ind-123",
                "income_chf": 95000,
                "marital_status": "single",
                "employment": "employed",
                "education_level": "tertiary",
            }
        ]
    }
    client.get_item.return_value = {
        "attributes": {
            "age": 34,
            "canton": "ZH",
            "city": "Zürich",
            "risk_appetite": "medium",
        }
    }
    return client


def test_list_individuals_enriches_with_state(mock_backend_client):
    service = NBAService(backend_client=mock_backend_client)
    individuals = service.list_individuals(limit=10)

    assert len(individuals) == 1
    ind = individuals[0]
    assert ind["individual_id"] == "ind-123"
    assert ind["income_chf"] == 95000
    assert ind["canton"] == "ZH"
    assert ind["age"] == 34
    assert ind["risk_appetite"] == "medium"
    mock_backend_client.list_collection.assert_called_once_with("individuals", limit=10, offset=0)
    mock_backend_client.get_item.assert_called_once_with("individual-states", "ind-123")


def test_get_individual_context(mock_backend_client):
    service = NBAService(backend_client=mock_backend_client)
    mock_backend_client.list_collection.side_effect = [
        {"items": [{"account_id": "acc-1"}]},
        {"items": [{"interaction_id": "int-1"}]},
    ]

    context = service.get_individual_context("ind-123")
    assert context["individual_id"] == "ind-123"
    assert "individual" in context
    assert "individual_state" in context
    assert len(context["accounts"]) == 1
    assert len(context["advisor_interactions"]) == 1


def test_evaluate_nba_caching(mock_backend_client):
    service = NBAService(backend_client=mock_backend_client)
    mock_result = {
        "individual_id": "ind-123",
        "recommended_action": "Offer Pillar 3a Retirement Account",
        "reasoning": "High income and low pension allocation.",
        "confidence": 0.88,
    }

    with patch("src.services.nba_service.build_agent") as mock_build:
        with patch("src.services.nba_service.evaluate_individual", return_value=mock_result) as mock_eval:
            # 1st call: Evaluates and populates cache
            res1 = service.evaluate_nba("ind-123")
            assert res1 == mock_result
            assert mock_eval.call_count == 1

            # 2nd call: Cache hit, does not call evaluate_individual again
            res2 = service.evaluate_nba("ind-123")
            assert res2 == mock_result
            assert mock_eval.call_count == 1

            # Force refresh: bypasses cache
            res3 = service.evaluate_nba("ind-123", force_refresh=True)
            assert res3 == mock_result
            assert mock_eval.call_count == 2


def test_clear_cache(mock_backend_client):
    service = NBAService(backend_client=mock_backend_client)
    service.cache["ind-123"] = {"recommended_action": "Test Action"}
    assert service.get_evaluated_count() == 1
    assert service.is_evaluated("ind-123") is True
    assert service.get_cached_nba("ind-123") == {"recommended_action": "Test Action"}

    service.clear_cache()
    assert service.get_evaluated_count() == 0
    assert service.is_evaluated("ind-123") is False
    assert service.get_cached_nba("ind-123") is None


def test_ask_advisor_assistant():
    service = NBAService()
    mock_agent = MagicMock()
    mock_agent.invoke.return_value = {
        "messages": [MagicMock(content="Here is the Next Best Action: Pillar 3a.")]
    }

    with patch.object(service, "get_advisor_agent", return_value=mock_agent):
        response = service.ask_advisor_assistant(
            inquiry_text="Was ist der NBA für ind-123?",
            dialogue_history=[{"role": "user", "content": "Hallo"}, {"role": "assistant", "content": "Wie kann ich helfen?"}],
        )
        assert "Pillar 3a" in response
        mock_agent.invoke.assert_called_once()

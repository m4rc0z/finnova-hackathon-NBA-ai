"""LangChain tools that expose the hackathon backend API to the agent.

See src/skills/nba_backend_skill.md for the full description of the backend.
"""

from langchain_core.tools import tool

from src.clients.backend_client import VALID_COLLECTIONS, BackendClient

_client = BackendClient()


def set_backend_base_url(base_url: str) -> None:
    """Update the backend base URL used across all backend tools."""
    global _client
    _client = BackendClient(base_url=base_url)


@tool
def check_health() -> dict:
    """Check whether the backend API is reachable and its data is loaded."""
    return _client.health()


@tool
def get_customer_features(individual_id: str) -> dict:
    """Get precomputed features for a customer (age, income_chf, employment,
    marital_status, num_accounts, has_savings, has_pillar3a,
    total_balance_chf, has_negative_balance, total_spent_chf,
    total_income_chf, num_transactions, top_spend_category,
    num_interactions, num_open_interactions, stress, ...), including a
    "product_inventory" dict with the exact product_names/kinds the
    customer already owns - use it for precise duplicate-product checks.

    Returns {"detail": "Individual not found"} if the individual_id is unknown.
    """
    return _client.get_customer_features(individual_id)


@tool
def get_recommendations(individual_id: str) -> dict:
    """Get scored next-best-action recommendations for a customer, produced
    by the backend's explainable rule-based scoring (not the offline ML
    model - see skill doc for the ML model's current status).

    Returns {"individual_id",
    "recommendations": [{"action", "score", "reasons"}],
    "product_suggestions": [{"action", "product_name", "score", "reasons"}]}
    both sorted by score, or {"detail": "Individual not found"} if unknown.
    Use product_suggestions to map a recommended action to a concrete
    product_name.
    """
    return _client.get_recommendations(individual_id)


@tool
def list_collection(
    collection: str,
    limit: int = 20,
    offset: int = 0,
    individual_id: str | None = None,
    account_id: str | None = None,
    run_id: str | None = None,
    period: int | None = None,
) -> dict:
    """List records from a backend collection, optionally filtered.

    collection must be one of: accounts, account-balances, employers,
    events, transactions, interactions, individuals, individual-states.
    Use individual_id/account_id to scope results to one customer/account.
    Use this for raw evidence (e.g. accounts, historical balances); prefer
    get_customer_features/get_recommendations for aggregated analysis.
    """
    if collection not in VALID_COLLECTIONS:
        return {"error": f"Unknown collection: {collection}", "valid_collections": sorted(VALID_COLLECTIONS)}
    return _client.list_collection(
        collection,
        limit=limit,
        offset=offset,
        run_id=run_id,
        period=period,
        individual_id=individual_id,
        account_id=account_id,
    )


@tool
def get_item(collection: str, item_id: str, run_id: str | None = None) -> dict:
    """Fetch a single record by id from a backend collection.

    collection must be one of: accounts, account-balances, employers,
    events, transactions, interactions, individuals, individual-states.
    item_id is the record's primary key (e.g. individual_id, account_id).
    Do not confuse account_id with individual_id - use the correct
    collection/id-field pairing (see skill doc).
    """
    if collection not in VALID_COLLECTIONS:
        return {"error": f"Unknown collection: {collection}", "valid_collections": sorted(VALID_COLLECTIONS)}
    return _client.get_item(collection, item_id, run_id=run_id)


BACKEND_TOOLS = [check_health, get_customer_features, get_recommendations, list_collection, get_item]

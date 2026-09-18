"""LangChain tools that expose the hackathon backend API to the agent.

See src/skills/nba_backend_skill.md for the full description of the backend.
"""

from langchain_core.tools import tool

from src.clients.backend_client import VALID_COLLECTIONS, BackendClient

_client = BackendClient()


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
    """
    if collection not in VALID_COLLECTIONS:
        return {"error": f"Unknown collection: {collection}", "valid_collections": sorted(VALID_COLLECTIONS)}
    return _client.get_item(collection, item_id, run_id=run_id)


BACKEND_TOOLS = [list_collection, get_item]

"""FastAPI backend server for Finnova NBA Hackathon API.

Implements the specification in src/skills/nba_backend_skill.md serving
collections: accounts, account-balances, employers, events, transactions,
interactions, individuals, individual-states.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
import pandas as pd

app = FastAPI(title="Finnova NBA Hackathon Backend API", version="1.0.0")

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "testdata"

ID_FIELDS = {
    "accounts": "account_id",
    "account-balances": "account_id",
    "employers": "employer_id",
    "events": "event_id",
    "transactions": "txn_id",
    "interactions": "interaction_id",
    "individuals": "individual_id",
    "individual-states": "individual_id",
}

# Cache loaded dataframes
_DATA_CACHE: dict[str, pd.DataFrame] = {}


def load_collection_df(collection: str) -> pd.DataFrame:
    if collection in _DATA_CACHE:
        return _DATA_CACHE[collection]

    file_mapping = {
        "individuals": "individual_state.csv",
        "individual-states": "individual.csv",
        "accounts": "account.csv",
        "account-balances": "account_balance.csv",
        "employers": "employer.csv",
        "interactions": "interaction.csv",
        "events": "event.csv",
        "transactions": "transaction_sample.csv" if (DATA_DIR / "transaction_sample.csv").exists() else "transaction.csv",
    }

    file_name = file_mapping.get(collection)
    if not file_name or not (DATA_DIR / file_name).exists():
        df = pd.DataFrame()
        _DATA_CACHE[collection] = df
        return df

    df = pd.read_csv(DATA_DIR / file_name).fillna("")
    if collection == "individuals" and "employment_type" in df.columns and "employment" not in df.columns:
        df["employment"] = df["employment_type"]

    _DATA_CACHE[collection] = df
    return df


def serialize_record(record: dict[str, Any], collection: str) -> dict[str, Any]:
    cleaned = {}
    for k, v in record.items():
        if v == "":
            cleaned[k] = None
        else:
            cleaned[k] = v

    # Parse JSON fields if present
    if collection == "individual-states" and "attributes" in cleaned and isinstance(cleaned["attributes"], str):
        try:
            cleaned["attributes"] = json.loads(cleaned["attributes"])
        except Exception:
            pass
    elif collection == "events" and "effects" in cleaned and isinstance(cleaned["effects"], str):
        try:
            cleaned["effects"] = json.loads(cleaned["effects"])
        except Exception:
            pass

    return cleaned


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "service": "finnova-nba-backend"}


@app.get("/api/v1/{collection}")
def list_collection(
    collection: str,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    run_id: str | None = None,
    period: int | None = None,
    individual_id: str | None = None,
    account_id: str | None = None,
) -> dict[str, Any]:
    if collection not in ID_FIELDS:
        raise HTTPException(status_code=400, detail=f"Unknown collection: {collection}")

    df = load_collection_df(collection)
    if df.empty:
        return {"collection": collection, "total": 0, "offset": offset, "limit": limit, "items": []}

    filtered = df
    if run_id and "run_id" in filtered.columns:
        filtered = filtered[filtered["run_id"] == run_id]
    if period is not None and "period" in filtered.columns:
        filtered = filtered[filtered["period"] == period]
    if individual_id and "individual_id" in filtered.columns:
        filtered = filtered[filtered["individual_id"] == individual_id]
    if account_id and "account_id" in filtered.columns:
        filtered = filtered[filtered["account_id"] == account_id]

    total = len(filtered)
    page_df = filtered.iloc[offset : offset + limit]
    items = [serialize_record(r, collection) for r in page_df.to_dict(orient="records")]

    return {
        "collection": collection,
        "total": total,
        "offset": offset,
        "limit": limit,
        "items": items,
    }


@app.get("/api/v1/{collection}/{item_id}")
def get_item(
    collection: str,
    item_id: str,
    run_id: str | None = None,
) -> Any:
    if collection not in ID_FIELDS:
        raise HTTPException(status_code=400, detail=f"Unknown collection: {collection}")

    id_col = ID_FIELDS[collection]
    df = load_collection_df(collection)
    if df.empty or id_col not in df.columns:
        raise HTTPException(status_code=404, detail="Item not found")

    matches = df[df[id_col].astype(str) == str(item_id)]
    if run_id and "run_id" in matches.columns:
        matches = matches[matches["run_id"] == run_id]

    if matches.empty:
        raise HTTPException(status_code=404, detail="Item not found")

    records = [serialize_record(r, collection) for r in matches.to_dict(orient="records")]

    if collection == "account-balances":
        return {"items": records}

    if len(records) > 1:
        return {"items": records}

    return records[0]

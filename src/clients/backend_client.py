"""HTTP client for the Finnova NBA hackathon backend (see src/skills/nba_backend_skill.md)."""

import os

import requests

VALID_COLLECTIONS = {
    "accounts",
    "account-balances",
    "employers",
    "events",
    "transactions",
    "interactions",
    "individuals",
    "individual-states",
}


class BackendClient:
    def __init__(self, base_url: str | None = None, timeout: float = 10.0):
        self.base_url = (base_url or os.getenv("BACKEND_BASE_URL", "http://localhost:8000")).rstrip("/")
        self.timeout = timeout

    def _get(self, path: str, params: dict | None = None) -> dict:
        response = requests.get(f"{self.base_url}{path}", params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def health(self) -> dict:
        return self._get("/health")

    def list_collection(
        self,
        collection: str,
        limit: int = 100,
        offset: int = 0,
        run_id: str | None = None,
        period: int | None = None,
        individual_id: str | None = None,
        account_id: str | None = None,
    ) -> dict:
        if collection not in VALID_COLLECTIONS:
            raise ValueError(f"Unknown collection: {collection}")
        params = {
            "limit": limit,
            "offset": offset,
            "run_id": run_id,
            "period": period,
            "individual_id": individual_id,
            "account_id": account_id,
        }
        params = {k: v for k, v in params.items() if v is not None}
        return self._get(f"/api/v1/{collection}", params=params)

    def get_item(self, collection: str, item_id: str, run_id: str | None = None) -> dict:
        if collection not in VALID_COLLECTIONS:
            raise ValueError(f"Unknown collection: {collection}")
        params = {"run_id": run_id} if run_id else None
        return self._get(f"/api/v1/{collection}/{item_id}", params=params)

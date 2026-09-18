"""NBA Service layer coordinating backend data retrieval, caching, and agent interactions."""

from __future__ import annotations

import logging
from typing import Any

from langchain.agents import create_agent

from src.agents.nba_agent import build_agent, evaluate_individual
from src.clients.backend_client import BackendClient
from src.clients.llm_client import get_llm
from src.tools.backend_tools import BACKEND_TOOLS, set_backend_base_url

logger = logging.getLogger(__name__)

ADVISOR_ASSISTANT_PROMPT = """You are an intelligent Next Best Action advisor assistant for retail banking.
Your role is to help bank advisors evaluate individuals and identify the single prioritized Next Best Action.

When answering inquiries:
- Use available backend tools to inspect individual records, individual states, accounts, account balances, recent transactions, and advisor interactions.
- Identify and formulate the single Next Best Action whenever applicable, grounded strictly in retrieved financial and individual state data.
- Maintain correct domain terminology: Individual, Next Best Action, Individual State, Advisor Interaction, Account Balance. Never refer to individuals as users, persons, or clients.
- Structure your response cleanly using Markdown (summary, reasoning, key metrics, and Next Best Action details).
"""


class NBAService:
    def __init__(self, backend_client: BackendClient | None = None):
        self.client = backend_client or BackendClient()
        if hasattr(self.client, "base_url") and self.client.base_url:
            set_backend_base_url(self.client.base_url)
        self._nba_cache: dict[str, dict[str, Any]] = {}
        self._advisor_agents: dict[str, Any] = {}

    @property
    def cache(self) -> dict[str, dict[str, Any]]:
        return self._nba_cache

    def clear_cache(self) -> None:
        self._nba_cache.clear()

    def get_cached_nba(self, individual_id: str) -> dict[str, Any] | None:
        return self._nba_cache.get(individual_id)

    def is_evaluated(self, individual_id: str) -> bool:
        return individual_id in self._nba_cache

    def get_evaluated_count(self) -> int:
        return len(self._nba_cache)

    def list_individuals(self, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        """List individuals and enrich them with their latest individual-state attributes."""
        try:
            res = self.client.list_collection("individuals", limit=limit, offset=offset)
            items = res.get("items", [])
            enriched = []
            for item in items:
                ind_id = item.get("individual_id")
                state = {}
                if ind_id:
                    try:
                        state_res = self.client.get_item("individual-states", ind_id)
                        if isinstance(state_res, dict):
                            state = state_res.get("attributes", state_res)
                    except Exception as err:
                        logger.debug(f"Failed to fetch state for {ind_id}: {err}")
                enriched.append({
                    "individual_id": ind_id,
                    "income_chf": item.get("income_chf"),
                    "marital_status": item.get("marital_status"),
                    "employment": item.get("employment"),
                    "education_level": item.get("education_level"),
                    "age": state.get("age") if isinstance(state, dict) else None,
                    "canton": state.get("canton") if isinstance(state, dict) else None,
                    "city": state.get("city") if isinstance(state, dict) else None,
                    "risk_appetite": state.get("risk_appetite") if isinstance(state, dict) else None,
                    "raw_individual": item,
                    "raw_state": state,
                })
            return enriched
        except Exception as e:
            logger.error(f"Error listing individuals from backend: {e}")
            raise

    def get_individual_context(self, individual_id: str) -> dict[str, Any]:
        """Fetch complete context for an individual across all collections."""
        context: dict[str, Any] = {"individual_id": individual_id}
        try:
            context["individual"] = self.client.get_item("individuals", individual_id)
        except Exception as e:
            context["individual"] = {"error": str(e)}

        try:
            context["individual_state"] = self.client.get_item("individual-states", individual_id)
        except Exception as e:
            context["individual_state"] = {"error": str(e)}

        try:
            context["accounts"] = self.client.list_collection("accounts", individual_id=individual_id).get("items", [])
        except Exception as e:
            context["accounts"] = []

        try:
            context["advisor_interactions"] = self.client.list_collection("interactions", individual_id=individual_id).get("items", [])
        except Exception as e:
            context["advisor_interactions"] = []

        return context

    def evaluate_nba(
        self,
        individual_id: str,
        provider: str | None = None,
        force_refresh: bool = False,
    ) -> dict[str, Any]:
        """Evaluate Next Best Action for an individual, leveraging the on-demand cache."""
        if not force_refresh and individual_id in self._nba_cache:
            return self._nba_cache[individual_id]

        set_backend_base_url(self.client.base_url)
        agent = build_agent(provider)
        result = evaluate_individual(agent, individual_id)
        self._nba_cache[individual_id] = result
        return result

    def get_advisor_agent(self, provider: str | None = None):
        """Build or return cached conversational advisor agent for the given provider."""
        key = (provider or "openai").lower()
        if key not in self._advisor_agents:
            set_backend_base_url(self.client.base_url)
            llm = get_llm(provider)
            self._advisor_agents[key] = create_agent(
                llm, tools=BACKEND_TOOLS, system_prompt=ADVISOR_ASSISTANT_PROMPT
            )
        return self._advisor_agents[key]

    def ask_advisor_assistant(
        self,
        inquiry_text: str,
        dialogue_history: list[dict[str, str]] | None = None,
        provider: str | None = None,
    ) -> str:
        """Process conversational query using the autonomous advisor agent."""
        agent = self.get_advisor_agent(provider)
        messages: list[dict[str, str]] = []
        if dialogue_history:
            for msg in dialogue_history:
                messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        messages.append({"role": "user", "content": inquiry_text})

        result = agent.invoke({"messages": messages})
        return result["messages"][-1].content

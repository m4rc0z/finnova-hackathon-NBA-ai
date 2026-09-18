"""Next Best Action (NBA) evaluation agent.

Given a dataset of individual_ids, the agent uses the backend tools
(src/tools/backend_tools.py) to gather customer context from the hackathon
backend and asks the configured LLM (OpenAI or Swisscom, see
src/clients/llm_client.py) to recommend and evaluate the next best action.
"""

import json

from dotenv import load_dotenv
from langchain.agents import create_agent

from src.clients.llm_client import get_llm
from src.tools.backend_tools import BACKEND_TOOLS

load_dotenv()

SYSTEM_PROMPT = """You are a Next Best Action (NBA) evaluation agent for a retail bank.

For a given individual_id, use the available tools to gather context:
- the individual's profile and attributes (individuals, individual-states)
- their accounts and balances (accounts, account-balances)
- recent transactions (transactions)
- past advisor interactions (interactions)

Then recommend the single next best action for this customer, grounded
only in the data you retrieved. Respond with a JSON object with keys:
"individual_id", "recommended_action", "reasoning", "confidence" (0-1).
"""


def build_agent(provider: str | None = None):
    llm = get_llm(provider)
    return create_agent(llm, tools=BACKEND_TOOLS, system_prompt=SYSTEM_PROMPT)


def evaluate_individual(agent, individual_id: str) -> dict:
    result = agent.invoke(
        {"messages": [{"role": "user", "content": f"Evaluate the next best action for individual_id={individual_id}."}]}
    )
    final_message = result["messages"][-1].content
    try:
        return json.loads(final_message)
    except json.JSONDecodeError:
        return {"individual_id": individual_id, "raw_response": final_message}


def evaluate_dataset(individual_ids: list[str], provider: str | None = None) -> list[dict]:
    """Run the NBA agent for each individual_id in the dataset."""
    agent = build_agent(provider)
    return [evaluate_individual(agent, individual_id) for individual_id in individual_ids]


if __name__ == "__main__":
    import sys

    ids = sys.argv[1:] or ["0002546a-e1aa-4023-b1e2-01b8e4c6fb93"]
    results = evaluate_dataset(ids)
    print(json.dumps(results, indent=2))

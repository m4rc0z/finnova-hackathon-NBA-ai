"""Example tool: get_available_client_attributes()"""

from typing import Any

from agents.tool import function_tool


def get_available_client_attributes_data() -> dict[str, Any]:
    """
    Return deterministic client attributes used by the example capability.

    In a real system, this data would come from a business capability or data
    source instead of this static proof-of-concept payload.
    """
    return {
        "client_id": "client_123",
        "name": "Acme Corp",
        "industry": "Technology",
        "annual_revenue": 5000000,
        "employee_count": 250,
        "location": "San Francisco, CA",
        "credit_score": 850,
        "relationship_length_months": 36,
        "available_products": [
            "business_credit_line",
            "trade_finance",
            "cash_management",
            "investment_advisory",
        ],
    }


@function_tool(description_override="Retrieve available client attributes and products")
def get_available_client_attributes() -> dict[str, Any]:
    """Return available client attributes for Agents SDK tool calling."""
    return get_available_client_attributes_data()

"""Tests for Tools."""

from agents.tool import FunctionTool

from nba_ai.tools.client_attrs import (
    get_available_client_attributes,
    get_available_client_attributes_data,
)


def test_tool_is_wrapped():
    """Test that the tool is properly wrapped as a FunctionTool."""
    # get_available_client_attributes should be a FunctionTool
    assert isinstance(get_available_client_attributes, FunctionTool)
    assert get_available_client_attributes.name == "get_available_client_attributes"


def test_tool_has_description():
    """Test that the tool has proper description."""
    assert "client attributes" in get_available_client_attributes.description.lower()


def test_tool_structure():
    """Test that the tool has expected JSON schema."""
    # The tool should have JSON schema for parameters
    assert isinstance(get_available_client_attributes.params_json_schema, dict)
    assert get_available_client_attributes.params_json_schema["type"] == "object"


def test_deterministic_tool_data():
    """Test the deterministic capability data used by the fallback."""
    result = get_available_client_attributes_data()

    assert result["client_id"] == "client_123"
    assert result["industry"] == "Technology"
    assert "business_credit_line" in result["available_products"]

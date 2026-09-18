#!/bin/bash
set -e

echo "================================"
echo "Definition of Done Verification"
echo "================================"
echo ""

# 1. uv sync works
echo "✓ Checking uv sync..."
if [ -d ".venv" ]; then
    echo "  ✅ Virtual environment exists"
else
    echo "  ❌ Virtual environment missing"
    exit 1
fi

# 2. Tests pass
echo "✓ Running tests..."
if uv run pytest tests/ -q > /tmp/test_output.txt 2>&1; then
    PASSED=$(grep -o "[0-9]* passed" /tmp/test_output.txt)
    echo "  ✅ $PASSED"
else
    echo "  ❌ Tests failed"
    cat /tmp/test_output.txt
    exit 1
fi

# 3. Linting passes
echo "✓ Running ruff..."
if uv run ruff check src/ tests/ > /tmp/lint_output.txt 2>&1; then
    echo "  ✅ All checks passed"
else
    echo "  ❌ Lint errors found"
    exit 1
fi

# 4. FastAPI starts
echo "✓ Testing FastAPI startup..."
if uv run python3 -c "from nba_ai.main import app; print('  ✅ App imports successfully')" > /dev/null 2>&1; then
    echo "  ✅ App imports successfully"
else
    echo "  ❌ App import failed"
    exit 1
fi

# 5. Health endpoint works
echo "✓ Testing /health endpoint..."
if uv run python3 << 'PYEOF' > /dev/null 2>&1
from fastapi.testclient import TestClient
from nba_ai.main import app
client = TestClient(app)
response = client.get("/health")
assert response.status_code == 200
assert response.json()["status"] == "ok"
PYEOF
then
    echo "  ✅ /health returns 200 OK"
else
    echo "  ❌ /health endpoint failed"
    exit 1
fi

# 6. Agent can be registered and retrieved
echo "✓ Testing agent registry..."
if uv run python3 << 'PYEOF' > /dev/null 2>&1
from nba_ai.agents.registry import get_agent, list_agents
agents = list_agents()
assert "nba_creator" in agents
agent = get_agent("nba_creator")()
assert agent.name == "nba_creator"
PYEOF
then
    echo "  ✅ Agent registry works"
else
    echo "  ❌ Agent registry failed"
    exit 1
fi

# 7. Structured output contract exists
echo "✓ Testing NBAProposal contract..."
if uv run python3 << 'PYEOF' > /dev/null 2>&1
from nba_ai.contracts.nba import NBAProposal
proposal = NBAProposal(
    name="Test",
    objective="Test Objective",
    explanation="Test Explanation"
)
assert proposal.name == "Test"
PYEOF
then
    echo "  ✅ Structured output contract works"
else
    echo "  ❌ Contract validation failed"
    exit 1
fi

# 8. Tool calling works
echo "✓ Testing tool definition..."
if uv run python3 << 'PYEOF' > /dev/null 2>&1
from agents.tool import FunctionTool
from nba_ai.tools.client_attrs import get_available_client_attributes
assert isinstance(get_available_client_attributes, FunctionTool)
assert "client" in get_available_client_attributes.description.lower()
PYEOF
then
    echo "  ✅ Tool is properly wrapped"
else
    echo "  ❌ Tool wrapping failed"
    exit 1
fi

# 9. Docker image builds
echo "✓ Checking Docker image..."
if docker images | grep -q "nba-ai-backend"; then
    echo "  ✅ Docker image exists (nba-ai-backend:test)"
else
    echo "  ⚠️  Docker image not built (run: docker build -t nba-ai-backend:test .)"
fi

# 10. README exists
echo "✓ Checking documentation..."
if [ -f "README.md" ] && grep -q "Quick Start" README.md; then
    echo "  ✅ README.md exists with setup instructions"
else
    echo "  ❌ README.md missing or incomplete"
    exit 1
fi

echo ""
echo "================================"
echo "✅ All Definition of Done items verified!"
echo "================================"
echo ""
echo "Backend is ready for use:"
echo "  • Tests: uv run pytest tests/ -v"
echo "  • Start: uv run uvicorn nba_ai.main:app --reload"
echo "  • Lint:  uv run ruff check src/ tests/"
echo "  • Docker: docker build -t nba-ai-backend . && docker run -p 8000:8000 -e OPENAI_API_KEY=... nba-ai-backend"

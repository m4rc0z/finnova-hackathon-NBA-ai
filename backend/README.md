# NBA AI Backend

Minimal Python agent runtime for **Next Best Action Studio** using OpenAI Agents SDK.

## Quick Start

### Prerequisites

- Python 3.12+
- `uv` (fast Python package manager)
- Swisscom API key for the OpenAI-compatible Apertus endpoint

### Local Setup

```bash
# Clone and navigate to backend
cd backend

# Install dependencies
uv sync

# Create .env from example
cp .env.example .env

# Edit .env and add your SWISSCOM_API_KEY
# (or set via environment variables)
```

### Running Locally

```bash
# Start FastAPI server
uv run uvicorn nba_ai.main:app --reload

# In another terminal, test the health endpoint
curl http://localhost:8000/health

# Run an agent with the Swisscom Apertus model
curl -X POST http://localhost:8000/api/agents/nba_creator/run \
  -H "Content-Type: application/json" \
  -d '{"input": "Analyze client Acme Corp and recommend next best actions"}'

# Discover agents managed by the orchestrator
curl http://localhost:8000/api/agents

# Run an agent through the orchestrator boundary
curl -X POST http://localhost:8000/api/orchestrator/run \
  -H "Content-Type: application/json" \
  -d '{"agent_name":"nba_creator","input":"Recommend a next best action for Acme Corp"}'
```

### Running Tests

```bash
# Run all tests (NO real API calls needed)
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=src/nba_ai

# Run specific test file
uv run pytest tests/test_registry.py -v
```

### Linting & Code Quality

```bash
# Check code style
uv run ruff check src/ tests/

# Auto-fix style issues
uv run ruff check src/ tests/ --fix
```

## Docker

Build and run in Docker (without OpenClaw):

```bash
# Build image
docker build -t nba-ai-backend:latest .

# Run container with the Swisscom configuration
docker run --env-file .env -p 8000:8000 \
  nba-ai-backend:latest

# Test health
curl http://localhost:8000/health
```

## Architecture

```
backend/
├── src/nba_ai/
│   ├── main.py                  # FastAPI app + endpoints
│   ├── config.py                # Settings from env vars
│   │
│   ├── agents/
│   │   ├── __init__.py          # Agent registration
│   │   ├── registry.py          # Simple agent lookup
│   │   └── nba_creator.py       # Example agent (PoC)
│   │
│   ├── contracts/
│   │   └── nba.py               # Pydantic: NBAProposal
│   │
│   ├── tools/
│   │   └── client_attrs.py      # Example tool: get_available_client_attributes()
│   │
│   └── services/
│       ├── agent_runtime.py     # run_agent() execution boundary
│       └── agent_orchestrator.py # discovery + delegation boundary
│
└── tests/                        # Unit tests (no API calls)
    ├── test_api.py              # FastAPI endpoints
    ├── test_agent_runtime.py    # Agent execution service
    ├── test_registry.py         # Agent registry
    ├── test_tools.py            # Tool definitions
    ├── test_contracts.py        # Pydantic models
    ├── test_orchestrator.py     # Orchestrator delegation
    └── conftest.py              # Pytest fixtures
```

## Key Design Decisions

1. **Agent Registry is Simple**
   - No OOP overhead, no reflection magic
   - Agents are stored as factory functions
   - Easy to extend with new agents

2. **Agent Runtime as Service Boundary**
   - `run_agent(agent_name, input, settings)` is the main entry point
   - The orchestrator delegates to this function
   - Keeps HTTP handlers clean and testable

3. **Deterministic Orchestrator**
   - `agent_orchestrator.py` lists registered agents and delegates selected runs
   - It does not generate Python code, persist agents, or run a supervisor loop
   - This keeps the first orchestration increment compatible with Swisscom Apertus

4. **No Agent Loop Re-implementation**
   - Uses OpenAI Agents SDK's `AgentRunner.run_sync()`
   - Agents are declarative (instructions, tools, output_type)
   - SDK handles model calls, tool execution, retries

5. **Structured Output via Pydantic**
   - Each agent declares its `output_type` (e.g., `NBAProposal`)
   - LLM response is automatically parsed into the Pydantic model
   - No manual JSON parsing

6. **Tool Calling with Function Tools**
   - Tools wrapped with `@function_tool` decorator
   - SDK automatically exposes them to the LLM
   - Agent decides when and how to use tools

7. **Tests Without API Calls**
   - All tests mock the LLM/runner
   - No test dependency on real OpenAI API
   - CI can run tests without secrets

## Configuration

Environment variables:
- `SWISSCOM_API_KEY`: Your Swisscom API key (required)
- `SWISSCOM_BASE_URL`: OpenAI-compatible Swisscom endpoint
- `SWISSCOM_MODEL`: Swisscom model identifier
- `LOG_LEVEL`: Logging level (default: `INFO`)

See `.env.example` for details.

The Swisscom Apertus endpoint is OpenAI-compatible for model calls, but its
current tool-calling behavior is model/provider dependent. The backend registers
the function tool and uses `tool_choice=auto`. For this deterministic proof of
concept, the same capability data is also supplied as a runtime fallback so the
agent can produce a concrete response when Apertus does not emit a tool call.

## Extending: Adding New Agents

1. **Create agent module**:
   ```python
   # src/nba_ai/agents/my_agent.py
   from agents import Agent
   from nba_ai.contracts.nba import NBAProposal
   
   def create_my_agent() -> Agent:
       return Agent(
           name="my_agent",
           instructions="Your instructions here",
           tools=[],  # Add tools
           output_type=NBAProposal,
       )
   ```

2. **Register in `__init__.py`**:
   ```python
   # src/nba_ai/agents/__init__.py
   from nba_ai.agents.my_agent import create_my_agent
   register_agent("my_agent", create_my_agent)
   ```

3. **Run via API**:
   ```bash
   curl -X POST http://localhost:8000/api/agents/my_agent/run \
     -H "Content-Type: application/json" \
     -d '{"input": "Your prompt"}'
   ```

## Extending: Adding New Tools

1. **Create tool function**:
   ```python
   # src/nba_ai/tools/my_tool.py
   from agents.tool import function_tool
   
   @function_tool(description_override="What this tool does")
   def my_tool(param1: str) -> dict:
       return {"result": f"Processed {param1}"}
   ```

2. **Add to agent**:
   ```python
   agent = Agent(
       name="my_agent",
       instructions="...",
       tools=[my_tool],
       output_type=NBAProposal,
   )
   ```

## Integration Points for OpenClaw/MCP

When OpenClaw is integrated later:

1. **Agent Orchestration**
   - OpenClaw can call `run_orchestrated_agent(agent_name, input, settings)`
   - Receives structured output (e.g., `NBAProposal`)
   - No need to change agent implementations

2. **MCP Adapter**
   - Could wrap `run_agent()` as MCP tool
   - Agent Registry becomes discoverable resource

3. **Potential Entry Point**
   ```python
   # openclaw_mcp_adapter.py (future)
   from nba_ai.services.agent_runtime import run_agent
   
   def mcp_run_agent_handler(agent_name, input_text):
       return run_agent(agent_name, input_text, settings)
   ```

## Known Limitations & TODOs

- ✅ Agents are synchronous only (sufficient for MVP)
- ✅ No persistence (agent runs are stateless)
- ✅ Tool output is JSON-serialized for LLM context (no binary/streaming)
- ⚠️ No authentication/authorization on endpoints (add API keys before production)
- ⚠️ No structured logging/observability backend (local console only)
- ⚠️ Single-model limitation (future: multi-model support)

## Testing Notes

- Unit tests DO NOT require `SWISSCOM_API_KEY`
- They mock agent execution and return deterministic outputs
- Manual smoke tests CAN be run explicitly with a real Swisscom API key
- To run the optional smoke tests:
  ```bash
  RUN_SWISSCOM_SMOKE=1 SWISSCOM_API_KEY=... uv run pytest tests/ -v -k "smoke"
  ```

## Common Issues

**"SWISSCOM_API_KEY is not set"**
- Create `.env` from `.env.example`
- Set `SWISSCOM_API_KEY=...`
- Or export: `export SWISSCOM_API_KEY=...`

**Tests fail with auth error**
- This shouldn't happen! Tests use mocks
- Check that `conftest.py` sets test env vars
- Run: `uv run pytest tests/test_api.py -v` to debug

**Docker container exits immediately**
- Check logs: `docker logs <container_id>`
- Ensure `SWISSCOM_API_KEY` is set in the container

## Future Work (Outside MVP Scope)

- [ ] Async agent execution (`run_agent` as async function)
- [ ] Session/conversation persistence (Database)
- [ ] Agent chaining & handoffs
- [ ] OpenClaw orchestrator integration
- [ ] MCP server wrapper
- [ ] Observability/tracing backend
- [ ] Multi-model selection per agent
- [ ] Input/output guardrails
- [ ] Real client data integration (DuckDB, Postgres)

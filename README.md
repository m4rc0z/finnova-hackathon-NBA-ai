# Finnova Next Best Action - Advisor Portal

Retail banking advisor platform evaluating financial context to determine prioritized Next Best Actions for individuals.

## Getting Started

### Prerequisites
- Python 3.14+ (managed via `uv`)
- Finnova Hackathon Backend running (default: `http://localhost:8000`)
- Valid OpenAI API key (or Swisscom credentials) in `.env`

### Installation
Sync dependencies:
```bash
uv sync
```

### Running the Frontend
Start the Streamlit advisor portal:
```bash
uv run streamlit run src/ui/app.py
```
By default, the UI will open at `http://localhost:8501`.

### Configuration
Set environment variables or configure them directly in the Streamlit sidebar:
- `BACKEND_BASE_URL`: URL of the hackathon backend (default: `http://localhost:8000`)
- `OPENAI_API_KEY`: API key for OpenAI
- `LLM_PROVIDER`: `openai` (default) or `swisscom`

### Running Tests
Execute unit tests:
```bash
uv run pytest
```

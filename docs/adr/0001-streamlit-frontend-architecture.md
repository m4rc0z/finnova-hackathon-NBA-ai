# 0001 Streamlit Frontend Architecture for Next Best Action

## Context
For the Finnova Next Best Action retail banking advisory prototype, bank advisors require an intuitive user interface to view prioritized Next Best Actions across individual portfolios and ask natural language inquiries grounded in individual financial context. The backend services and LangChain agents are authored in Python.

## Decision
We implement the frontend using Streamlit directly within the Python workspace. The interface provides two views:
1. Portfolio overview displaying individuals and on-demand cached Next Best Action evaluations.
2. An autonomous conversational advisor assistant allowing free-form inquiries about individuals, rationale, transactions, and life situations using the underlying backend tools.
Configuration for the backend API URL is managed through environment variables with sidebar override capabilities.

## Consequences
- Fast delivery without JavaScript/Node build complexity.
- Direct seamless reuse of existing Python LangChain agents and HTTP client tooling.
- Easy to run locally and demo in hackathon environments via `uv run streamlit run ...`.

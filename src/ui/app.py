"""Finnova Next Best Action - Advisor Portal (Streamlit Frontend)."""

import os
import sys
from pathlib import Path

# Ensure workspace root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pandas as pd
import streamlit as st

from src.clients.backend_client import BackendClient
from src.services.nba_service import NBAService
from src.tools.backend_tools import set_backend_base_url

st.set_page_config(
    page_title="Finnova - Next Best Action Advisor",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)


def format_confidence(confidence: float | None) -> str:
    """Format confidence score into percentage string."""
    if confidence is None:
        return "-"
    return f"{int(confidence * 100)}%"


def get_service(base_url: str) -> NBAService:
    if "nba_service" not in st.session_state or st.session_state.get("current_base_url") != base_url:
        set_backend_base_url(base_url)
        client = BackendClient(base_url=base_url)
        st.session_state.nba_service = NBAService(backend_client=client)
        st.session_state.current_base_url = base_url
    return st.session_state.nba_service


@st.cache_data(ttl=60, show_spinner=False)
def fetch_cached_individuals(base_url: str, limit: int = 50) -> list[dict]:
    client = BackendClient(base_url=base_url)
    service = NBAService(backend_client=client)
    return service.list_individuals(limit=limit)


def render_sidebar():
    st.sidebar.title("Finnova NBA Advisor")
    st.sidebar.caption("Retail Banking Advisory Platform")

    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Connection Settings")

    default_url = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")
    backend_url = st.sidebar.text_input("Backend Base URL", value=default_url)

    provider = st.sidebar.selectbox(
        "LLM Provider",
        options=["swisscom", "openai"],
        index=0 if os.getenv("LLM_PROVIDER", "swisscom").lower() == "swisscom" else 1,
    )
    os.environ["LLM_PROVIDER"] = provider

    if provider == "swisscom":
        default_sc_url = os.getenv(
            "SWISSCOM_BASE_URL",
            "https://api.swisscom.com/products/swiss-ai-weeks/apertus-1.5-70b/v1",
        )
        sc_base_url = st.sidebar.text_input(
            "Swisscom Base URL",
            value=default_sc_url,
        )
        sc_api_key = st.sidebar.text_input(
            "Swisscom API Key",
            value=os.getenv("SWISSCOM_API_KEY", ""),
            type="password",
            placeholder="Key hier einfügen...",
        )
        if sc_base_url:
            os.environ["SWISSCOM_BASE_URL"] = sc_base_url
        if sc_api_key:
            os.environ["SWISSCOM_API_KEY"] = sc_api_key
    elif provider == "openai":
        oa_api_key = st.sidebar.text_input(
            "OpenAI API Key",
            value=os.getenv("OPENAI_API_KEY", ""),
            type="password",
        )
        if oa_api_key:
            os.environ["OPENAI_API_KEY"] = oa_api_key

    service = get_service(backend_url)

    # Health check button
    if st.sidebar.button("Test Backend Connection"):
        try:
            health = service.client.health()
            st.sidebar.success(f"Connected: {health.get('status', 'OK')}")
        except Exception as e:
            st.sidebar.error(f"Connection failed: {e}")

    cached_count = service.get_evaluated_count()
    st.sidebar.metric("Evaluated Next Best Actions", cached_count)

    if st.sidebar.button("Clear NBA Cache"):
        service.clear_cache()
        st.sidebar.info("Cache cleared.")
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        **Domain Glossary**
        - **Individual**: Retail banking individual
        - **Next Best Action**: Single prioritized advisory action
        - **Individual State**: Snapshot of attributes, risk, and situation
        - **Advisor Interaction**: Engagement record across channels
        - **Account Balance**: Recorded monetary balance
        """
    )
    return service, provider, backend_url


def render_portfolio_view(service: NBAService, provider: str, backend_url: str):
    st.subheader("📋 Individuals Portfolio & Next Best Actions")
    st.caption("View individuals, demographic attributes, and on-demand Next Best Actions.")

    # Fetch Individuals using cached loader
    with st.spinner("Loading individuals from backend..."):
        try:
            individuals = fetch_cached_individuals(backend_url, limit=50)
        except Exception as err:
            st.error(
                f"Could not load individuals from backend at `{backend_url}`.\n\n"
                f"**Error Details**: {err}\n\n"
                "Please verify that the Finnova Hackathon backend is reachable, or update the Backend Base URL in the sidebar."
            )
            return

    if not individuals:
        st.warning("No individuals found in the backend.")
        return

    # Prepare DataFrame
    table_data = []
    for ind in individuals:
        ind_id = ind["individual_id"]
        cached_nba = service.get_cached_nba(ind_id)
        action_text = cached_nba.get("recommended_action", "Not Evaluated") if cached_nba else "Not Evaluated"
        confidence_val = cached_nba.get("confidence") if cached_nba else None

        table_data.append({
            "Individual ID": ind_id,
            "Age": ind.get("age") or "-",
            "Canton": ind.get("canton") or "-",
            "Income (CHF)": f"{ind.get('income_chf'):,}" if ind.get("income_chf") is not None else "-",
            "Employment": ind.get("employment") or "-",
            "Risk Appetite": ind.get("risk_appetite") or "-",
            "Next Best Action": action_text,
            "Confidence": format_confidence(confidence_val),
        })

    df = pd.DataFrame(table_data)

    total_col, eval_col, pending_col = st.columns(3)
    total_col.metric("Total Individuals Loaded", len(individuals))
    evaluated_count = sum(1 for ind in individuals if service.is_evaluated(ind["individual_id"]))
    eval_col.metric("Evaluated Next Best Actions", evaluated_count)
    pending_col.metric("Pending Evaluations", len(individuals) - evaluated_count)

    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("🔍 Individual Deep-Dive & Evaluation")

    individual_options = [ind["individual_id"] for ind in individuals]
    selected_id = st.selectbox("Select Individual ID for evaluation & details:", individual_options)

    if selected_id:
        trigger_col, status_col = st.columns([2, 1])
        with trigger_col:
            button_label = "🔄 Re-evaluate Next Best Action" if service.is_evaluated(selected_id) else "🚀 Evaluate Next Best Action"
            if st.button(button_label, key="eval_btn", type="primary"):
                with st.spinner(f"Evaluating Next Best Action for individual {selected_id}..."):
                    try:
                        service.evaluate_nba(selected_id, provider=provider, force_refresh=True)
                        st.success("Evaluation complete!")
                    except Exception as e:
                        st.error(f"Evaluation failed: {e}")
        with status_col:
            if service.is_evaluated(selected_id):
                st.info("Status: Evaluated & cached")

        # Display NBA Result Card if available
        cached_nba = service.get_cached_nba(selected_id)
        if cached_nba:
            st.markdown("#### 🎯 Next Best Action")
            with st.container(border=True):
                action_display_col, confidence_display_col = st.columns([3, 1])
                action_display_col.markdown(f"### **{cached_nba.get('recommended_action', 'N/A')}**")
                confidence_score = cached_nba.get("confidence")
                if confidence_score is not None:
                    confidence_display_col.metric("Confidence", format_confidence(confidence_score))

                st.markdown(f"**Reasoning:** {cached_nba.get('reasoning', 'No reasoning provided.')}")
                if "raw_response" in cached_nba:
                    st.text_area("Agent Response", cached_nba["raw_response"], height=100)

        # Context Details (Individual State, Accounts, Balances, Advisor Interactions)
        with st.expander("📊 View Individual Data (State, Accounts, Interactions)", expanded=False):
            with st.spinner("Fetching full individual context..."):
                ctx = service.get_individual_context(selected_id)

            tab_state, tab_accounts, tab_interactions = st.tabs(
                ["Individual & State", "Accounts & Account Balances", "Advisor Interactions"]
            )

            with tab_state:
                ind_col, state_col = st.columns(2)
                with ind_col:
                    st.write("**Individual Record:**", ctx.get("individual", {}))
                with state_col:
                    st.write("**Individual State Attributes:**", ctx.get("individual_state", {}))

            with tab_accounts:
                accounts = ctx.get("accounts", [])
                if accounts:
                    st.dataframe(pd.DataFrame(accounts), use_container_width=True, hide_index=True)
                else:
                    st.write("No accounts found.")

            with tab_interactions:
                interactions = ctx.get("advisor_interactions", [])
                if interactions:
                    st.dataframe(pd.DataFrame(interactions), use_container_width=True, hide_index=True)
                else:
                    st.write("No advisor interactions recorded.")


def render_chat_view(service: NBAService, provider: str):
    st.subheader("💬 Autonomous NBA Advisor Assistant")
    st.caption("Ask free-form questions about individuals, financial context, reasoning, or specific Next Best Actions.")

    # Initialize chat history
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": (
                    "Grüezi! Ich bin Ihr Finnova Next Best Action Berater-Assistent. "
                    "Fragen Sie mich nach Analysen, Hintergründen oder Next Best Actions zu einzelnen "
                    "Individuals oder nach allgemeinen Auswertungen."
                ),
            }
        ]

    # Quick prompt shortcuts
    with st.expander("💡 Beispielfragen zum Ausprobieren", expanded=False):
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        sample_id = "0002546a-e1aa-4023-b1e2-01b8e4c6fb93"
        if btn_col1.button("Next Best Action für Individual analysieren"):
            st.session_state.inquiry_input = f"Welche Next Best Action empfiehlst du für individual_id={sample_id} und warum?"
        if btn_col2.button("Risiko & Individual State prüfen"):
            st.session_state.inquiry_input = f"Überprüfe das Risikoprofil und bestehende Konten für individual_id={sample_id}."
        if btn_col3.button("Advisor Interactions zusammenfassen"):
            st.session_state.inquiry_input = f"Welche vergangenen Advisor Interactions gab es bei individual_id={sample_id}?"

    # Display past messages
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    prompt = st.chat_input("Ihre Frage an den NBA Advisor Assistant...")
    if "inquiry_input" in st.session_state and st.session_state.inquiry_input:
        prompt = st.session_state.inquiry_input
        st.session_state.inquiry_input = None

    if prompt:
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("NBA Assistant recherchiert und analysiert Daten..."):
                try:
                    response_text = service.ask_advisor_assistant(
                        inquiry_text=prompt,
                        dialogue_history=st.session_state.chat_messages[:-1],
                        provider=provider,
                    )
                    st.markdown(response_text)
                    st.session_state.chat_messages.append({"role": "assistant", "content": response_text})
                except Exception as e:
                    err_msg = f"Fehler bei der Beantwortung: {e}"
                    st.error(err_msg)
                    st.session_state.chat_messages.append({"role": "assistant", "content": err_msg})


def main():
    service, provider, backend_url = render_sidebar()

    tab_portfolio, tab_chat = st.tabs(["📋 Portfolio & Next Best Actions", "💬 Advisor Assistant (Chat)"])

    with tab_portfolio:
        render_portfolio_view(service, provider, backend_url)

    with tab_chat:
        render_chat_view(service, provider)


if __name__ == "__main__":
    main()

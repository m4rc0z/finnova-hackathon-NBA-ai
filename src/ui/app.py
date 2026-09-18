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
from src.ui.theme import CUSTOM_CSS

st.set_page_config(
    page_title="Alpha - Next Best Action Advisor",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


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


# Inline SVG path data extracted from the reference Alpha app (Lucide-style icons, stroke-width 1.65)
_NAV_ICON_PATHS = {
    "overview": "M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z",
    "clients": "M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M16 3a4 4 0 0 1 0 8M22 21v-2a4 4 0 0 0-3-3.87M13 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0",
    "my_day": "M8 2v4M16 2v4M3 9h18M5 4h14a2 2 0 0 1 2 2v14H3V6a2 2 0 0 1 2-2M7 13h3M14 13h3M7 17h3",
    "insights": "M3 17l6-6 4 3 8-10M15 4h6v6M3 3v18h18",
    "action_studio": "M12 3l2.4 6.6L21 12l-6.6 2.4L12 21l-2.4-6.6L3 12l6.6-2.4z",
    "life_goals": "M21 12a9 9 0 1 1-9-9M17 3l4 0 0 4M12 12l9-9M16 12a4 4 0 1 1-4-4",
    "roundup": "M3 8l4-4 4 4M7 4v12a4 4 0 0 0 4 4M21 16l-4 4-4-4M17 20V8a4 4 0 0 0-4-4",
    "governance": "M12 3l8 3v6c0 5-8 9-8 9s-8-4-8-9V6zM8 12l3 3 5-6",
    "assistant": "M21 11a8 8 0 0 1-8 8H6l-4 3 1.5-6A8 8 0 1 1 21 11M7 11h.01M12 11h.01M17 11h.01",
    "preferences": "M9 3h6l1 3 3 1 2 5-2 5-3 1-1 3H9l-1-3-3-1-2-5 2-5 3-1zM16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0",
    "search": "M21 21l-5-5M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0",
}


def _nav_icon(name: str, size: int = 18) -> str:
    path = _NAV_ICON_PATHS[name]
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="1.65" stroke-linecap="round" '
        f'stroke-linejoin="round"><path d="{path}"></path></svg>'
    )


def render_sidebar():
    st.sidebar.markdown(
        f"""
        <div class="alpha-logo">
            <div class="alpha-logo-badge">α</div>
            <div>
                <div class="alpha-logo-name">alpha</div>
                <div class="alpha-logo-by">by finnova</div>
            </div>
        </div>
        <div class="alpha-nav-section">Your workspace</div>
        <div class="alpha-nav-item">{_nav_icon('overview')} Overview</div>
        <div class="alpha-nav-item">{_nav_icon('clients')} Clients</div>
        <div class="alpha-nav-item">{_nav_icon('my_day')} My day</div>
        <div class="alpha-nav-section">Intelligence &amp; planning</div>
        <div class="alpha-nav-item active">{_nav_icon('insights')} Insights</div>
        <div class="alpha-nav-item">{_nav_icon('action_studio')} Action studio</div>
        <div class="alpha-nav-item">{_nav_icon('life_goals')} Life goals</div>
        <div class="alpha-nav-item">{_nav_icon('roundup')} Round-up investing</div>
        <div class="alpha-nav-item">{_nav_icon('governance')} Governance</div>
        <div class="alpha-nav-item">{_nav_icon('assistant')} Alpha assistant <span class="alpha-nav-badge">NEW</span></div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar.expander("Preferences", expanded=False, icon="⚙️"):
        st.caption("Retail Banking Advisory Platform - Connection Settings")

        default_url = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")
        backend_url = st.text_input("Backend Base URL", value=default_url)

        provider = st.selectbox(
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
            sc_base_url = st.text_input("Swisscom Base URL", value=default_sc_url)
            sc_api_key = st.text_input(
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
            oa_api_key = st.text_input(
                "OpenAI API Key",
                value=os.getenv("OPENAI_API_KEY", ""),
                type="password",
            )
            if oa_api_key:
                os.environ["OPENAI_API_KEY"] = oa_api_key

        service = get_service(backend_url)

        if st.button("Test Backend Connection"):
            try:
                health = service.client.health()
                st.success(f"Connected: {health.get('status', 'OK')}")
            except Exception as e:
                st.error(f"Connection failed: {e}")

        cached_count = service.get_evaluated_count()
        st.metric("Evaluated Next Best Actions", cached_count)

        if st.button("Clear NBA Cache"):
            service.clear_cache()
            st.info("Cache cleared.")
            st.rerun()

        st.markdown("---")
        st.markdown(
            """
            **Domain Glossary**
            - **Individual**: Retail banking individual
            - **Next Best Action**: Single prioritized advisory action
            - **Individual State**: Snapshot of attributes, risk, and situation
            - **Advisor Interaction**: Engagement record across channels
            - **Account Balance**: Recorded monetary balance
            """
        )

    st.sidebar.markdown(
        f"""
        <div class="alpha-workspace-card">
            <div class="alpha-workspace-title">{_nav_icon('governance', 14)} Evidence-led workspace</div>
            <div class="alpha-workspace-meta">Hackathon demo · September 2026<br>Human decisions. Clear boundaries.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return service, provider, backend_url


def render_portfolio_view(service: NBAService, provider: str, backend_url: str):
    st.markdown('<div class="alpha-eyebrow">FROM DATA TO DIALOGUE</div>', unsafe_allow_html=True)
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
                badge_col, action_display_col, confidence_display_col = st.columns([1, 2, 1])
                badge_col.markdown('<span class="alpha-badge">opportunity</span>', unsafe_allow_html=True)
                action_display_col.markdown(f"### **{cached_nba.get('recommended_action', 'N/A')}**")
                confidence_score = cached_nba.get("confidence")
                if confidence_score is not None:
                    confidence_display_col.metric("Confidence", format_confidence(confidence_score))

                st.markdown(f"**Reasoning:** {cached_nba.get('reasoning', 'No reasoning provided.')}")
                if "raw_response" in cached_nba:
                    st.text_area("Agent Response", cached_nba["raw_response"], height=100)

                st.markdown("---")
                feedback = service.get_feedback(selected_id)
                fb_useful_col, fb_dismiss_col, fb_label_col = st.columns([1, 1, 3])
                useful_label = "✓ Useful" if feedback != "useful" else "✓ Useful ✓"
                if fb_useful_col.button(useful_label, key=f"fb_useful_{selected_id}"):
                    service.record_feedback(selected_id, "useful")
                    st.rerun()
                if fb_dismiss_col.button("Dismiss", key=f"fb_dismiss_{selected_id}"):
                    service.record_feedback(selected_id, "dismissed")
                    st.rerun()
                fb_label_col.caption(f"Feedback: {feedback or 'not rated yet'}")

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


@st.dialog("💬 Ask Alpha", width="large")
def render_ask_alpha_dialog(service: NBAService, provider: str):
    render_chat_view(service, provider)


def render_ask_alpha_fab(service: NBAService, provider: str):
    """Floating 'Ask Alpha' button (bottom-right) that opens the chat as a popup."""
    with st.container(key="ask_alpha_fab"):
        if st.button("💬 Ask Alpha", key="ask_alpha_btn"):
            render_ask_alpha_dialog(service, provider)


def render_header():
    """Top breadcrumb/user bar, mirrors the source Alpha app's header."""
    search_icon = _nav_icon("search", 16)
    st.markdown(
        f"""
        <div class="alpha-header">
            <div class="alpha-header-breadcrumb">
                <span class="alpha-breadcrumb-root">Workspace</span>
                <span>›</span>
                <span class="alpha-breadcrumb-current">Insights</span>
            </div>
            <div class="alpha-header-actions">
                <span class="alpha-icon-btn">{search_icon} Search clients</span>
                <div class="alpha-avatar">JO</div>
                <div class="alpha-header-user"><strong>Your workspace</strong>Adviser · demo</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer():
    """Bottom footer, mirrors the source Alpha app's footer."""
    st.markdown(
        """
        <div class="alpha-footer">
            Alpha reimagined · Finnova hackathon 2026<br>
            Source-backed insights · Explicit simulations · Human review
        </div>
        """,
        unsafe_allow_html=True,
    )


def main():
    service, provider, backend_url = render_sidebar()

    render_header()
    render_portfolio_view(service, provider, backend_url)
    render_ask_alpha_fab(service, provider)
    render_footer()


if __name__ == "__main__":
    main()

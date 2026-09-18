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


def render_individual_card(service: NBAService, provider: str, ind: dict, key_prefix: str):
    """Render one individual as an Alpha-style insight card, with a
    'Create action →' link that triggers evaluation and opens the detail view."""
    ind_id = ind["individual_id"]
    cached_nba = service.get_cached_nba(ind_id)
    feedback = service.get_feedback(ind_id)

    with st.container(border=True):
        icon_col, badge_col = st.columns([1, 1])
        icon_col.markdown(_nav_icon("insights", 20), unsafe_allow_html=True)
        badge_text = "opportunity" if cached_nba else "pending"
        badge_col.markdown(
            f'<div style="text-align:right"><span class="alpha-badge">{badge_text}</span></div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<span class="alpha-eyebrow">{ind_id[:13]}… · {ind.get("age") or "-"}y · {ind.get("canton") or "-"}</span>',
            unsafe_allow_html=True,
        )
        title = cached_nba.get("recommended_action") if cached_nba else "Not yet evaluated"
        st.markdown(f"**{title}**")
        description = (
            cached_nba.get("reasoning")
            if cached_nba
            else "Click Create action to run the NBA agent for this individual."
        )
        st.caption(description[:160] + ("…" if len(description) > 160 else ""))

        st.markdown("---")
        if cached_nba:
            useful_col, dismiss_col = st.columns(2)
            if useful_col.button("✓ Useful", key=f"{key_prefix}_useful", type="primary" if feedback == "useful" else "secondary"):
                service.record_feedback(ind_id, "useful")
                st.rerun()
            if dismiss_col.button("Dismiss", key=f"{key_prefix}_dismiss", type="primary" if feedback == "dismissed" else "secondary"):
                service.record_feedback(ind_id, "dismissed")
                st.rerun()
        if st.button("Create action →", key=f"{key_prefix}_create"):
            st.session_state.selected_individual_id = ind_id
            if not cached_nba:
                with st.spinner("Evaluating Next Best Action..."):
                    try:
                        service.evaluate_nba(ind_id, provider=provider, force_refresh=False)
                    except Exception as e:
                        st.error(f"Evaluation failed: {e}")
            st.rerun()


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

    total_col, eval_col, pending_col = st.columns(3)
    total_col.metric("Total Individuals Loaded", len(individuals))
    evaluated_count = sum(1 for ind in individuals if service.is_evaluated(ind["individual_id"]))
    eval_col.metric("Evaluated Next Best Actions", evaluated_count)
    pending_col.metric("Pending Evaluations", len(individuals) - evaluated_count)

    st.markdown("---")

    display_limit = st.session_state.get("portfolio_display_limit", 9)
    visible_individuals = individuals[:display_limit]
    for row_start in range(0, len(visible_individuals), 3):
        row = visible_individuals[row_start : row_start + 3]
        cols = st.columns(3)
        for col, ind in zip(cols, row):
            with col:
                render_individual_card(service, provider, ind, key_prefix=f"card_{ind['individual_id']}")

    if display_limit < len(individuals):
        if st.button(f"Show more individuals ({len(individuals) - display_limit} remaining)"):
            st.session_state.portfolio_display_limit = display_limit + 9
            st.rerun()

    st.markdown("---")
    st.subheader("🔍 Individual Deep-Dive & Evaluation")

    selected_id = st.session_state.get("selected_individual_id")
    if not selected_id:
        st.info("Click **Create action →** on a card above to evaluate an individual and see full details here.")
        return

    reeval_col, status_col = st.columns([2, 1])
    with reeval_col:
        if st.button("🔄 Re-evaluate Next Best Action", key="reeval_btn"):
            with st.spinner(f"Evaluating Next Best Action for individual {selected_id}..."):
                try:
                    service.evaluate_nba(selected_id, provider=provider, force_refresh=True)
                except Exception as e:
                    st.error(f"Evaluation failed: {e}")
    with status_col:
        if service.is_evaluated(selected_id):
            st.caption("Status: Evaluated & cached")

    # Display NBA Result Card if available, styled like the source app's insight cards
    cached_nba = service.get_cached_nba(selected_id)
    if cached_nba:
        with st.container(border=True):
            badge_col, id_col, confidence_col = st.columns([1, 3, 1])
            badge_col.markdown('<span class="alpha-badge">opportunity</span>', unsafe_allow_html=True)
            id_col.markdown(f'<span class="alpha-eyebrow">{selected_id}</span>', unsafe_allow_html=True)
            confidence_score = cached_nba.get("confidence")
            if confidence_score is not None:
                confidence_col.metric("Confidence", format_confidence(confidence_score))

            st.markdown(f"### {cached_nba.get('recommended_action', 'N/A')}")
            st.markdown("---")
            st.markdown(f"**Suggested next step**  \n{cached_nba.get('reasoning', 'No reasoning provided.')}")
            if "raw_response" in cached_nba:
                with st.expander("Why am I seeing this?"):
                    st.text_area("Agent Response", cached_nba["raw_response"], height=100)

            st.markdown("---")
            feedback = service.get_feedback(selected_id)
            fb_useful_col, fb_dismiss_col, fb_label_col = st.columns([1, 1, 3])
            if fb_useful_col.button("✓ Useful", key=f"fb_useful_{selected_id}", type="primary" if feedback == "useful" else "secondary"):
                service.record_feedback(selected_id, "useful")
                st.rerun()
            if fb_dismiss_col.button("Dismiss", key=f"fb_dismiss_{selected_id}", type="primary" if feedback == "dismissed" else "secondary"):
                service.record_feedback(selected_id, "dismissed")
                st.rerun()
            if feedback == "useful":
                fb_label_col.markdown('<span class="alpha-feedback-badge useful">✓ Marked useful</span>', unsafe_allow_html=True)
            elif feedback == "dismissed":
                fb_label_col.markdown('<span class="alpha-feedback-badge dismissed">✕ Dismissed</span>', unsafe_allow_html=True)
            else:
                fb_label_col.caption("Feedback: not rated yet")

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

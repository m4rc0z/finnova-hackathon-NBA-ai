"""Custom CSS injected into the Streamlit app to mirror the 'Alpha' advisory
workspace design (dark navy theme, rounded cards, pill tabs/badges) - see
https://finnova-2617-web.ashyocean-d1992cc8.swedencentral.azurecontainerapps.io/
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --alpha-bg: #0E1420;
    --alpha-surface: #171F2E;
    --alpha-border: #2A3549;
    --alpha-text: #EDF2FF;
    --alpha-text-muted: #93A1BD;
    --alpha-accent: #7B9FFF;
    --alpha-accent-text: #0B1835;
    --alpha-radius-lg: 18px;
    --alpha-radius-sm: 10px;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: var(--alpha-bg) !important;
    color: var(--alpha-text) !important;
    font-family: 'Inter', Arial, Helvetica, sans-serif !important;
}

/* Hide Streamlit's Deploy button, hamburger menu and footer branding */
[data-testid="stToolbar"], #MainMenu, footer, [data-testid="stDecoration"] {
    display: none !important;
}

[data-testid="stSidebar"] {
    background-color: var(--alpha-surface) !important;
    border-right: 1px solid var(--alpha-border);
}

h1, h2, h3, h4 { color: var(--alpha-text) !important; font-weight: 600 !important; }
p, span, label, div { color: var(--alpha-text); }
.stCaption, [data-testid="stCaptionContainer"] { color: var(--alpha-text-muted) !important; }

/* Bordered containers -> Alpha cards */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: var(--alpha-surface) !important;
    border: 1px solid var(--alpha-border) !important;
    border-radius: var(--alpha-radius-lg) !important;
    padding: 4px;
}

/* Buttons -> Alpha pill buttons */
.stButton > button {
    background-color: #253656 !important;
    color: var(--alpha-accent) !important;
    border: 1px solid var(--alpha-border) !important;
    border-radius: var(--alpha-radius-sm) !important;
    font-weight: 500 !important;
}
.stButton > button:hover {
    border-color: var(--alpha-accent) !important;
    color: var(--alpha-text) !important;
}
.stButton > button[kind="primary"] {
    background-color: var(--alpha-accent) !important;
    color: var(--alpha-accent-text) !important;
    border: none !important;
}

/* Tabs -> Alpha pill tab-list */
[data-baseweb="tab-list"] {
    background-color: rgba(255,255,255,0.03);
    border-radius: 999px;
    padding: 4px;
    gap: 4px;
    border: 1px solid var(--alpha-border);
}
[data-baseweb="tab"] {
    border-radius: 999px !important;
    color: var(--alpha-text-muted) !important;
    font-weight: 500;
}
[aria-selected="true"][data-baseweb="tab"] {
    background-color: var(--alpha-surface) !important;
    color: var(--alpha-text) !important;
}

/* Metrics -> Alpha KPI card look */
[data-testid="stMetric"] {
    background-color: var(--alpha-surface);
    border: 1px solid var(--alpha-border);
    border-radius: var(--alpha-radius-lg);
    padding: 16px 20px;
}
[data-testid="stMetricLabel"] { color: var(--alpha-text-muted) !important; }

/* Badge pill helper (used via st.markdown) */
.alpha-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 999px;
    background-color: rgba(123, 159, 255, 0.15);
    color: var(--alpha-accent);
    font-size: 0.8rem;
    font-weight: 500;
}
.alpha-eyebrow {
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--alpha-text-muted);
    font-size: 0.75rem;
    font-weight: 600;
}
hr, .alpha-divider { border-color: var(--alpha-border) !important; }

/* Floating "Ask Alpha" button, sticky bottom-right, mirrors the source app's FAB.
   Uses `sticky` instead of `fixed` because Streamlit's internal wrappers
   apply CSS transforms, which would otherwise break fixed positioning. */
.st-key-ask_alpha_fab {
    position: sticky;
    bottom: 28px;
    z-index: 999;
    display: flex;
    justify-content: flex-end;
    margin-top: 24px;
    pointer-events: none;
}
.st-key-ask_alpha_fab .stButton {
    pointer-events: auto;
}
.st-key-ask_alpha_fab .stButton > button {
    background-color: var(--alpha-accent) !important;
    color: var(--alpha-accent-text) !important;
    border: none !important;
    border-radius: 999px !important;
    padding: 12px 22px !important;
    font-weight: 600 !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
}
</style>
"""

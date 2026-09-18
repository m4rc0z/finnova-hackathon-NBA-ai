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

/* Sidebar nav (mirrors the source app's workspace navigation) */
.alpha-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 4px 0 20px 0;
}
.alpha-logo-badge {
    width: 34px;
    height: 34px;
    border-radius: 10px;
    background-color: var(--alpha-accent);
    color: var(--alpha-accent-text);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 1.1rem;
}
.alpha-logo-name { font-weight: 700; font-size: 1.15rem; color: var(--alpha-text); }
.alpha-logo-by { font-size: 0.7rem; color: var(--alpha-text-muted); line-height: 1.1; }

.alpha-nav-section {
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--alpha-text-muted);
    font-size: 0.7rem;
    font-weight: 600;
    margin: 18px 4px 8px 4px;
}
.alpha-nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 12px;
    border-radius: 10px;
    color: var(--alpha-text-muted);
    font-weight: 500;
    font-size: 0.95rem;
    margin-bottom: 2px;
}
.alpha-nav-item.active {
    background-color: rgba(123, 159, 255, 0.15);
    color: var(--alpha-accent) !important;
    font-weight: 600;
}
.alpha-nav-item .alpha-nav-badge {
    margin-left: auto;
    font-size: 0.65rem;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 6px;
    background-color: rgba(255,255,255,0.08);
    color: var(--alpha-text-muted);
}
.alpha-nav-item svg { flex-shrink: 0; }
.alpha-workspace-card {
    border: 1px solid var(--alpha-border);
    border-radius: var(--alpha-radius-lg);
    padding: 14px 16px;
    margin-top: 24px;
}
.alpha-workspace-card .alpha-workspace-title {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #6EE7B7;
    font-weight: 700;
    margin-bottom: 6px;
}
.alpha-workspace-card .alpha-workspace-meta {
    color: var(--alpha-text-muted);
    font-size: 0.8rem;
    line-height: 1.4;
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

/* Top header bar (breadcrumb + workspace/user area), mirrors the source app */
.alpha-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 14px;
    margin-bottom: 6px;
    border-bottom: 1px solid var(--alpha-border);
}
.alpha-header-breadcrumb {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.85rem;
}
.alpha-header-breadcrumb .alpha-breadcrumb-root { color: var(--alpha-text-muted); }
.alpha-header-breadcrumb .alpha-breadcrumb-current { color: #70DABA; font-weight: 700; }
.alpha-header-actions {
    display: flex;
    align-items: center;
    gap: 16px;
}
.alpha-header-actions .alpha-icon-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    color: var(--alpha-text-muted);
    font-size: 0.85rem;
    padding: 6px 10px;
    border-radius: var(--alpha-radius-sm);
    border: 1px solid var(--alpha-border);
}
.alpha-avatar {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background-color: rgba(123, 159, 255, 0.15);
    color: var(--alpha-accent);
    font-size: 0.7rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
}
.alpha-header-user { font-size: 0.75rem; color: var(--alpha-text-muted); line-height: 1.2; }
.alpha-header-user strong { color: var(--alpha-text); display: block; font-size: 0.8rem; }

/* Bottom footer, mirrors the source app */
.alpha-footer {
    text-align: center;
    margin-top: 36px;
    padding-top: 18px;
    border-top: 1px solid var(--alpha-border);
    color: var(--alpha-text-muted);
    font-size: 0.75rem;
    line-height: 1.6;
}

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

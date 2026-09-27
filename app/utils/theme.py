"""
Smart Crop Advisory — shared premium visual-polish layer.

This module is PURELY presentational (CSS only). It does not touch any
model inference, database, authentication, or business logic anywhere
in the app. Every page can safely call `apply_premium_theme()` near the
top (after its own imports) to pick up a consistent, elevated look:
soft entrance animations, card hover-lift, glowing icon badges, nicer
buttons/tabs/progress-bars/tables/scrollbars, etc.

Nothing here renames or removes any existing CSS class used by the
pages — it only adds new rules (many targeting Streamlit's own
`data-testid` hooks) that layer on top of what already exists.
"""

import streamlit as st


PREMIUM_THEME_CSS = """
<style>
/* ============================================================
   SMART CROP ADVISORY — SHARED PREMIUM UI ENHANCEMENT LAYER
   Purely visual (CSS-only). Safe to include on every page.
   ============================================================ */

@keyframes scaFadeInUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* Smooth entrance for the whole page body on every rerun */
[data-testid="stAppViewContainer"] { animation: scaFadeInUp 0.35s ease both; }

/* Hero banners across every page get a soft ambient highlight + entrance */
.classify-hero, .farm-hero-banner, .weather-hero, .assistant-hero,
.help-hero, .market-header, .auth-hero, .dashboard-header,
.species-hero {
    position: relative;
    overflow: hidden;
    animation: scaFadeInUp 0.5s ease both;
}
.classify-hero::before, .farm-hero-banner::before, .weather-hero::before,
.assistant-hero::before, .help-hero::before, .market-header::before,
.auth-hero::before, .dashboard-header::before, .species-hero::before {
    content: "";
    position: absolute;
    top: -60%;
    right: -8%;
    width: 320px;
    height: 320px;
    background: radial-gradient(circle, rgba(255,255,255,0.16) 0%, rgba(255,255,255,0) 70%);
    pointer-events: none;
}

/* Card lift-on-hover, applied to every card-like surface site-wide */
.weather-card, .price-card, .stat-box, .action-card-btn, .adviser-card,
.assistant-panel, .glass-card, .user-card, .dashboard-welcome,
[data-testid="stVerticalBlockBorderWrapper"] {
    transition: transform 0.22s ease, box-shadow 0.22s ease !important;
}
.weather-card:hover, .price-card:hover, .stat-box:hover, .action-card-btn:hover,
.adviser-card:hover, .assistant-panel:hover, .user-card:hover,
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 14px 30px rgba(20, 60, 30, 0.12) !important;
}

/* Buttons: gentle lift + shadow bloom + smooth press, everywhere */
[data-testid="stButton"] button, [data-testid="stFormSubmitButton"] button {
    transition: transform 0.15s ease, box-shadow 0.15s ease, filter 0.15s ease !important;
    border-radius: 10px !important;
}
[data-testid="stButton"] button:hover, [data-testid="stFormSubmitButton"] button:hover {
    transform: translateY(-2px);
    filter: brightness(1.03);
}
[data-testid="stButton"] button:active, [data-testid="stFormSubmitButton"] button:active {
    transform: translateY(0px) scale(0.98);
}

/* Primary (type="primary") buttons: on-brand forest-green everywhere in the
   authenticated app, not just the login screen. Streamlit's own default for
   a primary button is red/coral, so this override applies site-wide. */
[data-testid="stButton"] button[kind="primary"],
[data-testid="stFormSubmitButton"] button[kind="primary"],
[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #1E5620 0%, #2D7D32 100%) !important;
    border: 1px solid #164318 !important;
    color: #ffffff !important;
    box-shadow: 0 6px 16px rgba(30,86,32,0.28) !important;
}
[data-testid="stButton"] button[kind="primary"] p,
[data-testid="stFormSubmitButton"] button[kind="primary"] p,
[data-testid="stButton"] button[kind="primary"] div,
[data-testid="stFormSubmitButton"] button[kind="primary"] div {
    color: #ffffff !important;
}
[data-testid="stButton"] button[kind="primary"]:hover,
[data-testid="stFormSubmitButton"] button[kind="primary"]:hover {
    background: linear-gradient(135deg, #216625 0%, #339139 100%) !important;
    border-color: #164318 !important;
}
[data-testid="stButton"] button[kind="primary"]:focus,
[data-testid="stFormSubmitButton"] button[kind="primary"]:focus {
    box-shadow: 0 0 0 0.2rem rgba(30,86,32,0.3) !important;
}

/* Icon badges (quick action icons, header logo icons) get a soft ambient glow */
.action-icon-wrap, .header-logo-icon, .login-mark, .admin-login-icon {
    box-shadow: 0 6px 16px rgba(30,86,32,0.22);
    transition: transform 0.2s ease;
}
.action-card-btn:hover .action-icon-wrap { transform: scale(1.08) rotate(-3deg); }

/* Tabs — consistent premium pill styling everywhere */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    border-radius: 12px !important;
    padding: 5px !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    box-shadow: 0 4px 14px rgba(0,0,0,0.10) !important;
}

/* Progress bars: crop-green gradient fill */
.stProgress > div > div > div > div {
    background-image: linear-gradient(90deg, #1E5620, #4CAF50) !important;
}

/* Alerts (success / error / info / warning) — rounder, softer, on-brand */
[data-testid="stAlert"] {
    border-radius: 14px !important;
    box-shadow: 0 6px 16px rgba(0,0,0,0.05);
}

/* Dataframe / table polish */
[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 6px 18px rgba(0,0,0,0.05);
}

/* Slim, on-brand scrollbars */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(30,86,32,0.35); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: rgba(30,86,32,0.55); }

/* Badges / pills used across pages: slightly bolder + tracked */
.badge-pending, .badge-answered, .hero-badge, .scheme-badge,
.stat-title-green, .stat-title-blue, .stat-title-purple, .stat-title-orange {
    letter-spacing: 0.3px;
}

/* Image frames: crisp rounded corners + soft border for uploaded/captured/result photos */
[data-testid="stImage"] img {
    border-radius: 14px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.08);
}

/* Expander polish */
[data-testid="stExpander"] {
    border-radius: 14px !important;
    overflow: hidden;
}

/* Stat / overview cards (Admin Panel) — accent top edge + gentle lift */
.stat-box { position: relative; overflow: hidden; }
.stat-box::after {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
}
.stat-box-green::after { background: linear-gradient(90deg, #16a34a, #4ade80); }
.stat-box-blue::after { background: linear-gradient(90deg, #2563eb, #60a5fa); }
.stat-box-purple::after { background: linear-gradient(90deg, #9333ea, #c084fc); }
.stat-box-orange::after { background: linear-gradient(90deg, #ea580c, #fb923c); }
</style>
"""


def apply_premium_theme():
    """Inject the shared Smart Crop Advisory visual-polish layer.

    Purely additive CSS — does not alter any widget behaviour, data,
    values, or layout structure. Safe to call at the top of every page,
    alongside that page's own existing <style> block.
    """
    st.markdown(PREMIUM_THEME_CSS, unsafe_allow_html=True)

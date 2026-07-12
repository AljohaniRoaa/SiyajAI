"""
سياج | Siyaj AI — PDPL & NDMO Compliance Auditor
==========================================
A single-file Streamlit application that scans uploaded CSV/Excel files,
dynamically infers the semantic type of each column via content-based
heuristics (regex), and produces an executive compliance dashboard graded
against:
  - PDPL (Personal Data Protection Law) — privacy / sensitive-data exposure
  - NDMO (National Data Management Office) — structural data governance quality

Author: Senior Data Governance Engineering (generated)
"""

import io
import re
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st

# ----------------------------------------------------------------------------
# Page configuration & light styling
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="سياج | Siyaj AI — PDPL & NDMO Compliance",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap" rel="stylesheet">
<style>
    :root {
        --ink: #0b1f3a;
        --ink-soft: #475569;
        --surface: #f6f8fb;
        --card: #ffffff;
        --border: #e7ebf2;
        --navy: #0b2545;
        --teal: #134e4a;
        --accent: #2563eb;
        --danger-a: #c56670; --danger-b: #954851;
        --warn-a: #b98136;   --warn-b: #96692a;
        --ok-a: #3f9d72;     --ok-b: #2c6e4e;
        --radius-lg: 18px;
        --radius-md: 14px;
        --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.06), 0 1px 1px rgba(15, 23, 42, 0.04);
        --shadow-md: 0 8px 24px rgba(15, 23, 42, 0.08), 0 2px 6px rgba(15, 23, 42, 0.04);
        --shadow-lg: 0 20px 45px rgba(11, 37, 69, 0.14);
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    /* ---- App canvas ---------------------------------------------------- */
    .stApp {
        background:
            radial-gradient(1200px 480px at 8% -8%, rgba(37,99,235,0.06), transparent 60%),
            var(--surface);
    }
    .main > div {padding-top: 1.4rem; padding-bottom: 2rem;}
    .block-container {padding-left: 2.4rem; padding-right: 2.4rem; max-width: 1360px;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}

    /* ---- Enterprise header banner --------------------------------------- */
    .govern-header {
        position: relative;
        background: linear-gradient(120deg, var(--navy) 0%, var(--teal) 100%);
        padding: 2.1rem 2.4rem;
        border-radius: var(--radius-lg);
        color: white;
        margin-bottom: 1.6rem;
        box-shadow: var(--shadow-lg);
        overflow: hidden;
    }
    .govern-header::after {
        content: "";
        position: absolute;
        inset: 0;
        background: radial-gradient(600px 200px at 90% 0%, rgba(255,255,255,0.10), transparent 65%);
        pointer-events: none;
    }
    .govern-header h1 {
        margin: 0;
        font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.01em;
    }
    .govern-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.88;
        font-size: 0.98rem;
        font-weight: 500;
    }
    .govern-header .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(255,255,255,0.14);
        border: 1px solid rgba(255,255,255,0.22);
        padding: 0.28rem 0.75rem;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 0.85rem;
    }

    /* ---- Risk / KPI cards ------------------------------------------------ */
    .risk-card {
        position: relative;
        border-radius: var(--radius-md);
        padding: 1.55rem 1.6rem 1.4rem;
        color: white;
        text-align: left;
        font-weight: 600;
        box-shadow: var(--shadow-md);
        border: 1px solid rgba(255,255,255,0.08);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .risk-card:hover {transform: translateY(-2px); box-shadow: var(--shadow-lg);}
    .risk-high   {background: linear-gradient(135deg, var(--danger-a), var(--danger-b));}
    .risk-medium {background: linear-gradient(135deg, var(--warn-a), var(--warn-b));}
    .risk-low    {background: linear-gradient(135deg, var(--ok-a), var(--ok-b));}
    .risk-card .card-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 30px;
        height: 30px;
        border-radius: 8px;
        background: rgba(255,255,255,0.16);
        border: 1px solid rgba(255,255,255,0.22);
        margin-bottom: 0.55rem;
    }
    .risk-card .card-icon svg {width: 16px; height: 16px; color: white;}
    .risk-card .card-label {font-size: 0.92rem;}
    .risk-card .big {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 2.1rem;
        font-weight: 800;
        display: block;
        margin-top: 0.35rem;
        letter-spacing: -0.01em;
    }
    div[data-testid="column"] {padding-left: 0.55rem; padding-right: 0.55rem;}

    /* ---- Section titles --------------------------------------------------- */
    .section-title {
        font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--ink);
        margin-top: 1.6rem;
        margin-bottom: 0.7rem;
        padding-bottom: 0.55rem;
        border-bottom: 1px solid var(--border);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* ---- Status badges ------------------------------------------------- */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        padding: 0.22rem 0.72rem;
        border-radius: 999px;
        font-size: 0.74rem;
        font-weight: 700;
        color: white;
        letter-spacing: 0.01em;
        box-shadow: var(--shadow-sm);
    }
    .badge-high   {background-color: var(--danger-a);}
    .badge-medium {background-color: var(--warn-a);}
    .badge-low    {background-color: var(--ok-a);}
    .badge-none   {background-color: #64748b;}

    /* ---- Sidebar --------------------------------------------------------- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0b1f3a 0%, #0b2545 100%);
        border-right: 1px solid var(--border);
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.6rem;
        padding-left: 1.3rem;
        padding-right: 1.3rem;
    }
    section[data-testid="stSidebar"] * {color: #e7edf7 !important;}
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.12) !important;
        margin: 1.1rem 0 !important;
    }
    section[data-testid="stSidebar"] .stCaption, section[data-testid="stSidebar"] small {
        color: #9fb0c9 !important;
        line-height: 1.5;
    }
    section[data-testid="stSidebar"] h2 {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 800;
        letter-spacing: -0.01em;
        margin-bottom: 0.1rem;
    }

    /* Sidebar brand row (logo mark + wordmark) */
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        margin-bottom: 0.15rem;
    }
    .sidebar-brand .logo-mark {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 34px;
        height: 34px;
        border-radius: 10px;
        background: rgba(96,165,250,0.16);
        border: 1px solid rgba(96,165,250,0.28);
        flex-shrink: 0;
    }
    .sidebar-brand .logo-mark svg {width: 18px; height: 18px; color: #93c5fd;}
    .sidebar-brand .wordmark {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 800;
        font-size: 1.18rem;
        letter-spacing: -0.01em;
        color: #f4f7fc !important;
    }

    /* Sidebar sub-labels (e.g. "Upload dataset") */
    .sidebar-label {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-weight: 700;
        font-size: 0.86rem;
        color: #cfe0f7 !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 0.55rem;
    }
    .sidebar-label svg {width: 14px; height: 14px; flex-shrink: 0; color: #60a5fa;}

    /* Upload card wrapper — makes the uploader stand out as a premium unit */
    section[data-testid="stSidebar"] div[data-testid="stFileUploader"] {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(96,165,250,0.22);
        border-radius: var(--radius-md);
        padding: 0.7rem;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.18);
    }

    /* File uploader dropzone */
    [data-testid="stFileUploaderDropzone"] {
        background: rgba(255,255,255,0.04) !important;
        border: 1.5px dashed rgba(255,255,255,0.28) !important;
        border-radius: var(--radius-md) !important;
        transition: border-color 0.15s ease, background 0.15s ease;
    }
    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: #60a5fa !important;
        background: rgba(96,165,250,0.08) !important;
    }
    section[data-testid="stSidebar"] button {
        background: #2563eb !important;
        color: white !important;
        border-radius: 10px !important;
        border: none !important;
        font-weight: 600 !important;
    }

    /* Uploaded file row — high-contrast light card with a file icon and
       graceful ellipsis truncation for long filenames. Selectors are scoped
       under the sidebar itself so they win over the sidebar's blanket
       light-text rule above (equal !important weight is decided by
       specificity, so these need to be at least as specific). Broad
       fallback selectors are kept for compatibility across Streamlit
       versions. */
    section[data-testid="stSidebar"] [data-testid="stFileUploaderFile"],
    section[data-testid="stSidebar"] [data-testid="stUploadedFile"],
    section[data-testid="stSidebar"] .uploadedFile {
        background: #ffffff !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        padding: 0.55rem 0.7rem !important;
        margin-top: 0.6rem !important;
        display: flex !important;
        align-items: center !important;
        gap: 0.55rem !important;
        box-shadow: var(--shadow-sm) !important;
        overflow: hidden !important;
        min-width: 0 !important;
        color: #000000 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stFileUploaderFile"]::before {
        content: "";
        flex-shrink: 0;
        width: 18px;
        height: 18px;
        background-repeat: no-repeat;
        background-position: center;
        background-size: contain;
        background-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%232563eb' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/%3E%3Cpolyline points='14 2 14 8 20 8'/%3E%3C/svg%3E");
    }
    section[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] *,
    section[data-testid="stSidebar"] [data-testid="stUploadedFile"] *,
    section[data-testid="stSidebar"] .uploadedFile * {
        color: #000000 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stFileUploaderFileName"],
    section[data-testid="stSidebar"] .uploadedFileName {
        color: #000000 !important;
        font-weight: 700 !important;
        font-size: 0.86rem !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
        max-width: 100% !important;
        min-width: 0 !important;
        display: block !important;
    }
    section[data-testid="stSidebar"] [data-testid="stFileUploaderFile"] small,
    section[data-testid="stSidebar"] [data-testid="stUploadedFile"] small {
        color: var(--ink-soft) !important;
    }

    /* Sidebar detection-engine list with icon chips */
    .detect-list {
        list-style: none;
        margin: 0;
        padding: 0;
        display: flex;
        flex-direction: column;
        gap: 0.55rem;
    }
    .detect-list li {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-size: 0.87rem;
        color: #dbe6f7 !important;
    }
    .detect-list .icon-chip {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 26px;
        height: 26px;
        border-radius: 8px;
        background: rgba(96,165,250,0.14);
        border: 1px solid rgba(96,165,250,0.24);
        flex-shrink: 0;
    }
    .detect-list .icon-chip svg {width: 14px; height: 14px; color: #93c5fd;}

    /* ---- Cards / containers for main content ------------------------------ */
    div[data-testid="stTabs"] {margin-top: 0.4rem;}
    button[data-baseweb="tab"] {
        font-weight: 600;
        font-size: 0.92rem;
        border-radius: 10px 10px 0 0 !important;
        padding: 0.6rem 1.1rem !important;
    }
    div[data-testid="stDataFrame"], div[data-testid="stTable"] {
        border-radius: var(--radius-md);
        overflow: hidden;
        border: 1px solid var(--border);
        box-shadow: var(--shadow-sm);
    }
    div[data-baseweb="tab-panel"] {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 0 var(--radius-md) var(--radius-md) var(--radius-md);
        padding: 1.5rem 1.6rem;
        box-shadow: var(--shadow-sm);
    }

    /* Metrics */
    div[data-testid="stMetric"] {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 0.9rem 1.1rem;
        box-shadow: var(--shadow-sm);
    }
    div[data-testid="stMetricLabel"] {color: var(--ink-soft) !important; font-weight: 600;}
    div[data-testid="stMetricValue"] {color: var(--navy) !important; font-family: 'Plus Jakarta Sans', sans-serif;}

    /* Generic buttons */
    .stButton button, .stDownloadButton button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        box-shadow: var(--shadow-sm);
    }

    /* Alerts (info / warning / error) */
    div[data-testid="stAlert"] {
        border-radius: var(--radius-md);
        border: 1px solid var(--border);
        box-shadow: var(--shadow-sm);
    }

    /* Landing "how it works" card wrapper */
    .how-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 1.6rem 1.8rem;
        box-shadow: var(--shadow-sm);
        margin-top: 0.8rem;
    }
    .how-card h4 {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: var(--navy);
        margin-top: 0;
    }

    h1, h2, h3 {font-family: 'Plus Jakarta Sans', 'Inter', sans-serif; color: var(--ink);}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# FIX: force visible (black) text across the main app body.
# Some Streamlit themes/environments render body text in a color that
# matches the background, making it invisible until selected/highlighted.
# This override forces black text everywhere in .stApp EXCEPT inside the
# sidebar, which intentionally uses light text (#e7edf7) against its own
# dark navy background defined above — excluding it avoids making sidebar
# text invisible against its dark background.
# ----------------------------------------------------------------------------
FORCE_TEXT_COLOR_CSS = """
<style>
    .stApp :not(section[data-testid="stSidebar"]):not(section[data-testid="stSidebar"] *) {
        color: #000000 !important;
    }

    /* Exceptions to the black-text override above: */

    /* 1) Keep the header title + subtitle white (they sit on the dark
          navy/teal gradient banner, so black text would be invisible). */
    .govern-header,
    .govern-header h1,
    .govern-header p,
    .govern-header * {
        color: #ffffff !important;
    }

    /* 2) Keep the inline `05` / `+966` code snippets (in the "how it
          works" panel) green. */
    .how-card code {
        color: #16a34a !important;
    }
</style>
"""
st.markdown(FORCE_TEXT_COLOR_CSS, unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Inline SVG icon library (presentation only)
# ----------------------------------------------------------------------------
# Small, dependency-free line icons (Lucide-style) used in place of emoji so
# that every icon renders identically across browsers/operating systems
# instead of relying on platform emoji fonts (which is what caused the
# National ID glyph to display incorrectly).
ICONS = {
    "shield": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2 4 5v6c0 5 3.4 8.7 8 11 4.6-2.3 8-6 8-11V5z"/></svg>',
    "folder": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>',
    "id_card": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="5" width="20" height="14" rx="2"/><circle cx="8" cy="12" r="2"/><line x1="6" y1="16.5" x2="10" y2="16.5"/><line x1="13" y1="9.5" x2="18" y2="9.5"/><line x1="13" y1="13.5" x2="18" y2="13.5"/></svg>',
    "phone": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="7" y="2" width="10" height="20" rx="2"/><line x1="11" y1="18" x2="13" y2="18"/></svg>',
    "mail": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 6 10 7 10-7"/></svg>',
    "landmark": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="21" x2="21" y2="21"/><path d="M4 21V10M9 21V10M15 21V10M20 21V10"/><path d="m2 10 10-6 10 6z"/></svg>',
    "database": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5"/><path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/></svg>',
    "lock": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>',
    "alert_triangle": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3 10 18H2z"/><line x1="12" y1="9" x2="12" y2="14"/><line x1="12" y1="17" x2="12" y2="17"/></svg>',
}


def icon(name: str) -> str:
    """Return inline SVG markup for a given icon key (presentation helper only)."""
    return ICONS.get(name, "")

# ----------------------------------------------------------------------------
# Regex heuristics
# ----------------------------------------------------------------------------
# NOTE: All patterns use non-capturing groups (?:...) and are only ever used
# with .str.contains() / .str.match() (never .extract()) so there is no risk
# of the pandas "this pattern has match groups" UserWarning or associated
# extraction errors.

PATTERNS = {
    # Saudi National ID / Iqama: exactly 10 digits, conventionally starting
    # with 1 (Saudi national) or 2 (resident/Iqama).
    "national_id": re.compile(r"^(?:1|2)\d{9}$"),
    # Generic 10-digit numeric sequence (fallback identity-like number that
    # doesn't match the Saudi ID prefix convention, e.g. account/ID numbers).
    "generic_10_digit": re.compile(r"^\d{10}$"),
    # Saudi mobile numbers: 05xxxxxxxx, +9665xxxxxxxx, 9665xxxxxxxx,
    # or 5xxxxxxxx (9 digits, no leading 0) with optional separators.
    "phone": re.compile(
        r"^(?:\+?966[\s\-]?5\d{8}|0?5\d{8})$"
    ),
    # Email — presence of '@' plus a plausible domain shape.
    "email": re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$"),
    # IBAN (Saudi) — useful bonus signal for financial sensitive data.
    "iban": re.compile(r"^SA\d{2}[A-Z0-9]{18}$", re.IGNORECASE),
    # Date of birth-like strings (very loose, just for structural signal).
    "date_like": re.compile(r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}$"),
}

SENSITIVE_TYPES = {"Identity/ID (National ID)", "Phone Number", "Email", "Bank/IBAN"}

# Headers that suggest sensitive PDPL "special category" data by name alone
# (used only as a secondary structural signal, not a replacement for content
# scanning).
SENSITIVE_NAME_HINTS = [
    "religion", "race", "ethnic", "health", "medical", "diagnosis",
    "criminal", "conviction", "biometric", "genetic", "political",
    "disability", "nationality_origin",
]

GENERIC_HEADER_PATTERN = re.compile(r"^(unnamed|column|col|field)[\s_:\-]?\d*$", re.IGNORECASE)


# ----------------------------------------------------------------------------
# Column type inference
# ----------------------------------------------------------------------------
def _clean_series_as_str(series: pd.Series) -> pd.Series:
    """Return a string-coerced version of a series with NaNs dropped, stripped."""
    s = series.dropna().astype(str).str.strip()
    # Remove common formatting characters before pattern matching so that
    # '966-5x-xxx-xxxx' or '05 xxx xxxx' style entries still match.
    s = s.str.replace(r"[\s\-\(\)]", "", regex=True)
    return s


def infer_column_type(series: pd.Series, col_name: str, sample_cap: int = 500) -> dict:
    """
    Infer the semantic type of a column purely from its *content* (never
    trusting the header name for classification — the header is only used
    as a secondary structural-quality hint elsewhere).

    Returns a dict with: type, confidence, match_rate, examples_masked
    """
    non_null = series.dropna()
    total = len(series)
    if total == 0 or non_null.empty:
        return {"type": "Empty/Unknown", "confidence": 0.0, "match_rate": 0.0, "n_checked": 0}

    cleaned = _clean_series_as_str(non_null)
    if len(cleaned) > sample_cap:
        cleaned = cleaned.sample(sample_cap, random_state=42)
    n_checked = len(cleaned)
    if n_checked == 0:
        return {"type": "Empty/Unknown", "confidence": 0.0, "match_rate": 0.0, "n_checked": 0}

    # Run each heuristic using .str.contains() (regex full-match anchored
    # patterns already include ^...$, so contains() behaves as a full match
    # here while remaining immune to capture-group extraction errors).
    rates = {}
    for label, pattern in PATTERNS.items():
        try:
            hits = cleaned.str.contains(pattern, regex=True, na=False)
            rates[label] = hits.mean()
        except re.error:
            rates[label] = 0.0

    threshold = 0.55  # majority of non-null values must match to classify

    # Priority order matters: National ID before generic 10-digit,
    # Email/Phone/IBAN are distinctive enough to check independently.
    if rates.get("national_id", 0) >= threshold:
        return {"type": "Identity/ID (National ID)", "confidence": rates["national_id"],
                "match_rate": rates["national_id"], "n_checked": n_checked}
    if rates.get("email", 0) >= threshold:
        return {"type": "Email", "confidence": rates["email"],
                "match_rate": rates["email"], "n_checked": n_checked}
    if rates.get("iban", 0) >= threshold:
        return {"type": "Bank/IBAN", "confidence": rates["iban"],
                "match_rate": rates["iban"], "n_checked": n_checked}
    if rates.get("phone", 0) >= threshold:
        return {"type": "Phone Number", "confidence": rates["phone"],
                "match_rate": rates["phone"], "n_checked": n_checked}
    if rates.get("generic_10_digit", 0) >= threshold:
        return {"type": "Identity/ID (Generic 10-digit)", "confidence": rates["generic_10_digit"],
                "match_rate": rates["generic_10_digit"], "n_checked": n_checked}
    if rates.get("date_like", 0) >= threshold:
        return {"type": "Date", "confidence": rates["date_like"],
                "match_rate": rates["date_like"], "n_checked": n_checked}

    # Fall back to pandas dtype based classification.
    if pd.api.types.is_numeric_dtype(series):
        return {"type": "Numeric (General)", "confidence": 1.0, "match_rate": 1.0, "n_checked": n_checked}

    avg_len = cleaned.str.len().mean() if not cleaned.empty else 0
    if avg_len and avg_len > 60:
        return {"type": "Free Text", "confidence": 0.6, "match_rate": 0.0, "n_checked": n_checked}

    return {"type": "Categorical/Text (General)", "confidence": 0.5, "match_rate": 0.0, "n_checked": n_checked}


def scan_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Run inference across every column and return a tidy results table."""
    rows = []
    for col in df.columns:
        info = infer_column_type(df[col], col)
        missing = df[col].isna().sum()
        missing_pct = (missing / len(df) * 100) if len(df) else 0
        name_hint_hit = any(h in str(col).lower() for h in SENSITIVE_NAME_HINTS)
        rows.append({
            "Column": col,
            "Inferred Type": info["type"],
            "Match Confidence": round(info["match_rate"] * 100, 1),
            "Missing Values": int(missing),
            "Missing %": round(missing_pct, 1),
            "Sensitive (PDPL)": (info["type"] in SENSITIVE_TYPES) or name_hint_hit,
            "Generic Header": bool(GENERIC_HEADER_PATTERN.match(str(col).strip())),
        })
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------
# Compliance grading engine
# ----------------------------------------------------------------------------
def grade_pdpl_privacy(scan_df: pd.DataFrame, df: pd.DataFrame) -> dict:
    """
    Grade PDPL privacy risk based on presence of unmasked identity/contact
    data. Assumes data found "as-is" in the file is unmasked unless it
    already looks pseudonymized (e.g. mostly non-matching / hashed values,
    which infer_column_type would have already excluded).
    """
    sensitive_cols = scan_df[scan_df["Sensitive (PDPL)"]]["Column"].tolist()
    id_cols = scan_df[scan_df["Inferred Type"].str.contains("Identity/ID", na=False)]["Column"].tolist()
    contact_cols = scan_df[scan_df["Inferred Type"].isin(["Email", "Phone Number"])]["Column"].tolist()
    bank_cols = scan_df[scan_df["Inferred Type"] == "Bank/IBAN"]["Column"].tolist()

    findings = []
    score = 0  # higher = worse

    if id_cols:
        score += 40
        findings.append(f"Unmasked national ID / identity numbers detected in: {', '.join(id_cols)}.")
    if contact_cols:
        score += 30
        findings.append(f"Personal contact information (email/phone) detected in: {', '.join(contact_cols)}.")
    if bank_cols:
        score += 30
        findings.append(f"Financial account identifiers (IBAN) detected in: {', '.join(bank_cols)}.")

    name_hint_cols = scan_df[scan_df["Generic Header"] == False][  # noqa: E712
        scan_df["Column"].str.lower().apply(lambda c: any(h in c for h in SENSITIVE_NAME_HINTS))
    ]["Column"].tolist() if not scan_df.empty else []
    if name_hint_cols:
        score += 20
        findings.append(
            f"Column headers suggest special-category data under Art. 1 sensitive data "
            f"definitions (health, religion, ethnicity, criminal record, etc.): {', '.join(name_hint_cols)}."
        )

    if score == 0:
        findings.append("No unmasked identity numbers, contact details, or special-category "
                         "data indicators were detected in this file.")

    if score >= 60:
        level = "High"
    elif score >= 25:
        level = "Medium"
    else:
        level = "Low"

    return {
        "level": level,
        "score": min(score, 100),
        "findings": findings,
        "sensitive_columns": sensitive_cols,
    }


def grade_ndmo_governance(scan_df: pd.DataFrame, df: pd.DataFrame) -> dict:
    """
    Grade NDMO structural governance quality: missing values, header
    hygiene (generic/unnamed columns), duplicate rows, and empty columns.
    """
    findings = []
    score = 0  # higher = worse

    total_cols = len(scan_df)
    empty_cols = scan_df[scan_df["Inferred Type"] == "Empty/Unknown"]["Column"].tolist()
    generic_header_cols = scan_df[scan_df["Generic Header"]]["Column"].tolist()
    high_missing_cols = scan_df[scan_df["Missing %"] >= 30]["Column"].tolist()
    dup_rows = int(df.duplicated().sum()) if not df.empty else 0
    avg_missing = scan_df["Missing %"].mean() if total_cols else 0

    if empty_cols:
        score += 20
        findings.append(f"Fully empty / unusable columns found: {', '.join(empty_cols)}.")
    if generic_header_cols:
        score += 20
        findings.append(
            f"Non-descriptive or auto-generated headers found (poor metadata hygiene): "
            f"{', '.join(generic_header_cols)}."
        )
    if high_missing_cols:
        score += 25
        findings.append(f"Columns with ≥30% missing values (data completeness risk): {', '.join(high_missing_cols)}.")
    if dup_rows > 0:
        dup_pct = round(dup_rows / len(df) * 100, 1) if len(df) else 0
        score += 15 if dup_pct < 10 else 25
        findings.append(f"{dup_rows} duplicate row(s) detected ({dup_pct}% of the dataset).")
    if avg_missing >= 15:
        score += 10
        findings.append(f"Average missingness across all columns is {round(avg_missing,1)}%, above the 15% guidance threshold.")

    if score == 0:
        findings.append("Headers are descriptive, missing-value levels are within tolerance, "
                         "and no duplicate rows or empty columns were found.")

    if score >= 55:
        level = "High"
    elif score >= 25:
        level = "Medium"
    else:
        level = "Low"

    return {
        "level": level,
        "score": min(score, 100),
        "findings": findings,
        "duplicate_rows": dup_rows,
    }


def overall_risk(pdpl_level: str, ndmo_level: str) -> str:
    order = {"Low": 0, "Medium": 1, "High": 2}
    return max([pdpl_level, ndmo_level], key=lambda x: order[x])


# ----------------------------------------------------------------------------
# UI helpers
# ----------------------------------------------------------------------------
def risk_card(label: str, level: str, subtitle: str, icon_key: str = "shield"):
    css_class = {"High": "risk-high", "Medium": "risk-medium", "Low": "risk-low"}.get(level, "risk-low")
    st.markdown(
        f"""
        <div class="risk-card {css_class}">
            <div class="card-icon">{icon(icon_key)}</div>
            <div class="card-label">{label}</div>
            <span class="big">{level}</span>
            <div style="font-size:0.78rem; opacity:0.9; margin-top:0.3rem;">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def badge(level: str) -> str:
    css = {"High": "badge-high", "Medium": "badge-medium", "Low": "badge-low"}.get(level, "badge-none")
    return f'<span class="badge {css}">{level}</span>'


def mask_preview(series: pd.Series, col_type: str) -> pd.Series:
    """Produce a masked preview for sensitive columns so the dashboard never
    displays raw personal data on screen."""
    def _mask(v):
        if pd.isna(v):
            return v
        v = str(v)
        if len(v) <= 4:
            return "*" * len(v)
        return v[:2] + "*" * (len(v) - 4) + v[-2:]
    if col_type in SENSITIVE_TYPES:
        return series.apply(_mask)
    return series


# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        f"""
        <div class="sidebar-brand">
            <div class="logo-mark">{icon('shield')}</div>
            <div class="wordmark">سياج | Siyaj AI</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("PDPL & NDMO Compliance Auditor")
    st.markdown("---")
    st.markdown(
        f'<div class="sidebar-label">{icon("folder")}<span>Upload dataset</span></div>',
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader(
        "Upload a dataset",
        type=["csv", "xlsx", "xls"],
        help="Upload a CSV or Excel file to run an automated compliance audit.",
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown("**Detection engine covers:**")
    st.markdown(
        f"""
        <ul class="detect-list">
            <li><span class="icon-chip">{icon('id_card')}</span> Saudi National ID / Iqama (10-digit)</li>
            <li><span class="icon-chip">{icon('phone')}</span> Saudi mobile numbers (05xx / +966 5xx)</li>
            <li><span class="icon-chip">{icon('mail')}</span> Email addresses</li>
            <li><span class="icon-chip">{icon('landmark')}</span> IBAN / bank identifiers</li>
            <li><span class="icon-chip">{icon('database')}</span> Structural data quality (NDMO)</li>
        </ul>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.caption(
        "This tool provides an automated, heuristic-based indication of "
        "potential PDPL/NDMO risk areas. It does not constitute legal advice "
        "and does not replace a full compliance review."
    )

# ----------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="govern-header">
        <div class="eyebrow">🛡️ Enterprise Compliance Suite</div>
        <h1>سياج | Siyaj AI — Data Governance &amp; Compliance Dashboard</h1>
        <p>Automated PDPL (privacy) &amp; NDMO (governance) audit engine · Report generated {datetime.now().strftime('%d %b %Y, %H:%M')}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if uploaded_file is None:
    st.info("👈 Upload a CSV or Excel file from the sidebar to begin the compliance audit.")
    st.markdown(
        """
<div class="how-card">
        <h4>How سياج | Siyaj AI works</h4>

1. **Dynamic column mapping** — every column's *content* (not its header) is scanned
   with regex heuristics to infer whether it holds an ID, phone number, email, or other data type.
2. **Heuristic engine** — distinguishes a Saudi National ID (10-digit, starts with 1 or 2)
   from a general phone number (Saudi `05` / `+966` mobile prefix) and other numeric fields.
3. **Compliance engine** — grades the file against PDPL (privacy exposure) and
   NDMO (structural governance quality) and produces High / Medium / Low risk ratings.
4. **Executive dashboard** — clean, presentation-ready summary with masked previews
   so no raw sensitive data is displayed on screen.

</div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# ----------------------------------------------------------------------------
# Load file
# ----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_file(file) -> pd.DataFrame:
    name = file.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)


try:
    with st.spinner("Loading and parsing file..."):
        df = load_file(uploaded_file)
except Exception as e:
    st.error(f"Could not read the uploaded file: {e}")
    st.stop()

if df.empty:
    st.warning("The uploaded file contains no rows.")
    st.stop()

# ----------------------------------------------------------------------------
# Run scan
# ----------------------------------------------------------------------------
with st.spinner("Running dynamic column mapping and heuristic engine..."):
    scan_df = scan_dataframe(df)
    pdpl_result = grade_pdpl_privacy(scan_df, df)
    ndmo_result = grade_ndmo_governance(scan_df, df)
    overall = overall_risk(pdpl_result["level"], ndmo_result["level"])

# ----------------------------------------------------------------------------
# Executive summary
# ----------------------------------------------------------------------------
st.markdown('<div class="section-title">📊 Executive Summary</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4, gap="large")
with c1:
    risk_card("Overall Compliance Risk", overall, f"{df.shape[0]:,} rows · {df.shape[1]} columns", icon_key="shield")
with c2:
    risk_card("PDPL — Privacy Risk", pdpl_result["level"], f"Score {pdpl_result['score']}/100", icon_key="lock")
with c3:
    risk_card("NDMO — Governance Risk", ndmo_result["level"], f"Score {ndmo_result['score']}/100", icon_key="database")
with c4:
    n_sensitive = len(pdpl_result["sensitive_columns"])
    risk_card("Sensitive Columns Found", "High" if n_sensitive else "Low",
              f"{n_sensitive} of {df.shape[1]} columns", icon_key="alert_triangle")

st.markdown("<br>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Tabs
# ----------------------------------------------------------------------------
tab_overview, tab_pdpl, tab_ndmo, tab_data = st.tabs(
    ["📊 Column Mapping", "🔒 PDPL Findings", "🗂️ NDMO Findings", "🧾 Masked Data Preview"]
)

with tab_overview:
    st.markdown('<div class="section-title">🧬 Dynamic Column Mapping Results</div>', unsafe_allow_html=True)
    st.caption("Column type is inferred from cell *content*, not the header name.")

    display_scan = scan_df.copy()
    display_scan["Sensitive (PDPL)"] = display_scan["Sensitive (PDPL)"].map({True: "⚠️ Yes", False: "No"})
    display_scan["Generic Header"] = display_scan["Generic Header"].map({True: "⚠️ Yes", False: "No"})
    st.dataframe(display_scan, use_container_width=True, hide_index=True)

    type_counts = scan_df["Inferred Type"].value_counts().reset_index()
    type_counts.columns = ["Inferred Type", "Count"]
    st.bar_chart(type_counts.set_index("Inferred Type"))

with tab_pdpl:
    st.markdown('<div class="section-title">🔒 PDPL — Privacy Risk Findings</div>', unsafe_allow_html=True)
    st.markdown(f"**Risk Level:** {badge(pdpl_result['level'])}  &nbsp;|&nbsp; **Score:** {pdpl_result['score']}/100",
                unsafe_allow_html=True)
    st.markdown("###### Findings")
    for f in pdpl_result["findings"]:
        st.markdown(f"- {f}")

    if pdpl_result["sensitive_columns"]:
        st.markdown("###### Applicable PDPL Guidance")
        st.markdown(
            "- Ensure a **documented lawful basis** exists for each of the columns above (Art. 5 / Art. 6).\n"
            "- Sensitive personal data (health, religion, criminal record, biometric, genetic, etc.) "
            "requires **explicit consent** if consent is the lawful basis, and **cannot** rely on legitimate interest.\n"
            "- Apply **pseudonymization or anonymization** where the identified purpose does not require raw values.\n"
            "- Confirm a **privacy notice** is provided to data subjects covering these data elements."
        )

with tab_ndmo:
    st.markdown('<div class="section-title">🗂️ NDMO — Data Governance Findings</div>', unsafe_allow_html=True)
    st.markdown(f"**Risk Level:** {badge(ndmo_result['level'])}  &nbsp;|&nbsp; **Score:** {ndmo_result['score']}/100",
                unsafe_allow_html=True)
    st.markdown("###### Findings")
    for f in ndmo_result["findings"]:
        st.markdown(f"- {f}")

    m1, m2, m3 = st.columns(3)
    m1.metric("Duplicate Rows", ndmo_result["duplicate_rows"])
    m2.metric("Avg. Missingness", f"{scan_df['Missing %'].mean():.1f}%")
    m3.metric("Generic Headers", int(scan_df["Generic Header"].sum()))

with tab_data:
    st.markdown('<div class="section-title">🧾 Masked Data Preview</div>', unsafe_allow_html=True)
    st.caption("Sensitive columns are automatically masked in this preview to prevent on-screen exposure of raw personal data.")
    preview_df = df.head(50).copy()
    type_lookup = dict(zip(scan_df["Column"], scan_df["Inferred Type"]))
    for col in preview_df.columns:
        preview_df[col] = mask_preview(preview_df[col], type_lookup.get(col, ""))
    st.dataframe(preview_df, use_container_width=True, hide_index=True)

# ----------------------------------------------------------------------------
# Footer note
# ----------------------------------------------------------------------------
st.markdown("---")
st.caption(
    "سياج | Siyaj AI is an automated screening tool for indicative PDPL/NDMO risk assessment. "
    "Findings are heuristic and should be validated by a qualified data protection officer "
    "before use in a formal compliance decision."
)
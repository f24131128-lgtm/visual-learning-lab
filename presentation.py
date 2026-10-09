"""Owned product styling; static tokens shared with fixed iframe renderers."""
from html import escape
import streamlit as st
from i18n import LANGUAGE_NAMES, current_language, tr

PLOT_STYLE = dict(foreground="#26332e", grid="#e4e9e3", axis="#adb8b0")

TOKENS = """
:root {
 --vll-page:#f8f9f6; --vll-raised:#ffffff; --vll-subtle:#eff2ee;
 --vll-fg:#26332e; --vll-muted:#59675f; --vll-faint:#647168;
 --vll-accent:#216653; --vll-accent-subtle:#e4efe9;
 --vll-evidence:#85642c; --vll-exploration:#216653;
 --vll-warning:#91601b; --vll-error:#ae3c37; --vll-border:#d9dfd9; --vll-focus:#26745f;
 --vll-space-1:4px; --vll-space-2:8px; --vll-space-3:12px; --vll-space-4:16px;
 --vll-space-6:24px; --vll-space-8:32px; --vll-space-12:48px;
 --vll-width:1440px; --vll-home-width:880px; --vll-radius-sm:4px; --vll-radius:8px;
 --vll-shadow:0 2px 8px #26332e08; --vll-shadow-raised:0 6px 24px #26332e0c;
 --vll-text-xs:12px; --vll-text-sm:14px; --vll-text:16px; --vll-title:24px; --vll-display:32px;
 --vll-control:36px; --vll-touch:44px; --vll-fast:120ms; --vll-calm:180ms;
 --vll-ease:cubic-bezier(.2,0,0,1); --vll-z-base:0; --vll-z-toolbar:10; --vll-z-overlay:20;
}
"""
STYLES = "<style>" + TOKENS + """
html,body,.stApp,input,textarea,button {font-family:"Noto Sans TC","PingFang TC","Microsoft JhengHei",system-ui,sans-serif}
.stApp {background:var(--vll-page);color:var(--vll-fg)}
.block-container {max-width:var(--vll-width);padding:3.5rem 2.5rem 2rem}
.block-container:has(.vll-home) {max-width:var(--vll-home-width)}
[data-testid="stHeader"] {background:var(--vll-page)}
[data-testid="stMarkdownContainer"] p,[data-testid="stMarkdownContainer"] li {font-size:var(--vll-text-sm);line-height:1.7;overflow-wrap:anywhere}
[data-testid="stMarkdownContainer"] h2 {font-size:var(--vll-title)}
[data-testid="stMarkdownContainer"] h3 {font-size:21px}
[data-testid="stMarkdownContainer"] h4 {font-size:18px}
h1,h2,h3,h4 {color:var(--vll-fg);font-weight:600;letter-spacing:-.025em;line-height:1.4}
[data-testid="stCaptionContainer"] p {font-size:var(--vll-text-xs);color:var(--vll-muted);line-height:1.6}
[data-testid="stWidgetLabel"] p {font-size:var(--vll-text-sm);font-weight:500}
[data-testid="stText"] {font-size:var(--vll-text-sm);line-height:1.6;overflow-wrap:anywhere}
.vll-brand {display:flex;align-items:center;gap:var(--vll-space-3);min-height:var(--vll-control);font-size:16px;font-weight:600;letter-spacing:-.025em}
.vll-mark {display:inline-block;width:22px;height:22px;border:1px solid var(--vll-accent);border-radius:2px;position:relative}
.vll-mark:after {content:"";position:absolute;inset:4px;border-left:1px solid var(--vll-accent);border-bottom:1px solid var(--vll-accent)}
.vll-home {padding:var(--vll-space-8) 0 var(--vll-space-4)}
.vll-home h1 {font-size:clamp(24px,3.2vw,32px);max-width:26em;padding:0 0 var(--vll-space-3)}
.vll-home p {color:var(--vll-muted);margin:0}
.st-key-product-header {padding-bottom:var(--vll-space-3);border-bottom:1px solid var(--vll-border)}
.st-key-material-input {padding:var(--vll-space-4) 0}
[data-testid="stFileUploaderDropzone"] {background:var(--vll-raised);border:1px dashed var(--vll-border);border-radius:var(--vll-radius)}
[data-baseweb="textarea"],[data-baseweb="select"] > div {background:var(--vll-raised);border-color:var(--vll-border);border-radius:var(--vll-radius-sm)}
div.stButton > button {min-height:var(--vll-control);border-radius:var(--vll-radius-sm);border-color:var(--vll-border);transition:background var(--vll-fast) var(--vll-ease),border-color var(--vll-fast) var(--vll-ease)}
div.stButton > button p {font-size:var(--vll-text-sm)}
div.stButton > button[kind="primary"] {background:var(--vll-accent);border-color:var(--vll-accent);color:white}
div.stButton > button[kind="secondary"] {background:var(--vll-raised);color:var(--vll-fg)}
div.stButton > button[kind="tertiary"] {border-color:transparent;color:var(--vll-muted)}
div.stButton > button:hover:not(:disabled) {border-color:var(--vll-accent);color:var(--vll-accent);background:var(--vll-accent-subtle)}
button:focus-visible,input:focus-visible,textarea:focus-visible,[role="radio"]:focus-visible {outline:2px solid var(--vll-focus)!important;outline-offset:3px}
button:disabled {opacity:.45;cursor:not-allowed}
.st-key-workspace-nav {border-bottom:1px solid var(--vll-border);padding-bottom:var(--vll-space-2)}
.st-key-workspace-nav [role="radiogroup"] {gap:var(--vll-space-2)}
.st-key-workspace-nav label {padding:6px 16px;border-radius:var(--vll-radius-sm);margin:0;color:var(--vll-muted)}
.st-key-workspace-nav label:has(input:checked) {background:var(--vll-accent-subtle);color:var(--vll-accent);box-shadow:inset 0 -2px var(--vll-accent)}
.st-key-workspace-nav label > div:first-child {display:none}
.st-key-workspace-nav label:focus-within {outline:2px solid var(--vll-focus);outline-offset:2px}
.st-key-context-rail {border-left:1px solid var(--vll-border);padding-left:var(--vll-space-6)}
[data-testid="stExpander"] details {border-color:var(--vll-border);border-radius:var(--vll-radius-sm);background:transparent}
[data-testid="stExpander"] summary {font-size:var(--vll-text-sm);color:var(--vll-muted)}
[data-testid="stMetricValue"] {font-size:22px;font-variant-numeric:tabular-nums}
.vll-twin-title {font-size:12px;letter-spacing:.08em;color:var(--vll-accent);padding-top:8px}
.vll-readout {width:100%;border-collapse:collapse;font-size:12px;font-variant-numeric:tabular-nums}
.vll-readout th {font-weight:500;color:var(--vll-muted);text-align:right;padding:8px 3px;border:0;border-bottom:1px solid var(--vll-border)}
.vll-readout td {text-align:right;padding:10px 3px;overflow-wrap:anywhere;border:0}
.vll-readout tr {background:transparent!important}
.vll-readout th:first-child,.vll-readout td:first-child {text-align:left}
.vll-readout td:nth-child(3) {color:var(--vll-exploration);font-weight:600}
.vll-readout td:nth-child(2) {color:var(--vll-muted)}
.vll-footer {border-top:1px solid var(--vll-border);padding-top:var(--vll-space-4);margin-top:var(--vll-space-8);color:var(--vll-faint);font-size:12px}
@media(max-width:900px) {
 .block-container {padding-left:20px;padding-right:20px}
 .st-key-learning-stage > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] {flex-wrap:wrap}
 .st-key-learning-stage > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {width:100%;flex:1 1 100%;min-width:0}
 .st-key-context-rail {border-left:0;border-top:1px solid var(--vll-border);padding:var(--vll-space-4) 0}
}
@media(max-width:600px) {
 .block-container {padding:3.5rem 16px 1.5rem}
 .st-key-product-header [data-testid="stHorizontalBlock"] {flex-wrap:nowrap}
 .st-key-product-header [data-testid="stColumn"] {min-width:0!important}
 .vll-brand {font-size:14px;gap:8px}
 .st-key-workspace-nav label {padding:8px 12px}
 div.stButton > button {min-height:var(--vll-touch)}
}
@media(prefers-reduced-motion:reduce) {*,*::before,*::after {transition:none!important;animation:none!important;scroll-behavior:auto!important}}
</style>
"""


def render_header():
    st.markdown(STYLES, unsafe_allow_html=True)
    with st.container(key="product-header"):
        brand, language = st.columns([3, 1])
        with brand:
            st.markdown('<div class="vll-brand"><span class="vll-mark" aria-hidden="true"></span>Visual Learning Lab</div>', unsafe_allow_html=True)
        with language:
            st.selectbox("語言 / Language", options=list(LANGUAGE_NAMES),
                         index=list(LANGUAGE_NAMES).index(current_language()),
                         format_func=LANGUAGE_NAMES.get, key="product_language", label_visibility="collapsed")
    if not st.session_state.get("analysis"):
        st.markdown(f'<div class="vll-home"><h1>{escape(tr("Turn complex material into something you can explore."))}</h1><p>{escape(tr("Bring a page, a chapter, or an idea you want to understand."))}</p></div>', unsafe_allow_html=True)


def material_input():
    """Keep widgets mounted; navigation does not retire input state."""
    return st.expander(tr("Change material"), expanded=False) if st.session_state.get("analysis") else st.container(key="material-input")


def render_footer():
    st.markdown(f'<div class="vll-footer">Visual Learning Lab · {escape(tr("Read. Explore. Understand."))}</div>', unsafe_allow_html=True)

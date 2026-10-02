"""Small shared typography layer and localized, familiar homepage framing."""

import streamlit as st

from i18n import LANGUAGE_NAMES, current_language, tr

STYLES = """
<style>
html, body, .stApp, [data-testid="stMarkdownContainer"], input, textarea, button {
  font-family: "Noto Sans TC", "PingFang TC", "Microsoft JhengHei", system-ui, sans-serif;
}
.block-container { max-width: 1040px; padding-top: 2rem; padding-bottom: 3rem; }
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li {
  font-size: 1.02rem; line-height: 1.8; font-weight: 450; overflow-wrap: anywhere;
}
[data-testid="stMarkdownContainer"] p { margin-bottom: .8rem; }
[data-testid="stMarkdownContainer"] h2 { font-size: 1.8rem; }
[data-testid="stMarkdownContainer"] h3 { font-size: 1.5rem; }
[data-testid="stMarkdownContainer"] h4 { font-size: 1.2rem; }
[data-testid="stMarkdownContainer"] h5 { font-size: 1.08rem; }
h1, h2, h3, h4, h5 { font-weight: 700; line-height: 1.45; letter-spacing: .01em; }
[data-testid="stCaptionContainer"] { color: inherit; }
[data-testid="stCaptionContainer"] p { font-size: .93rem; line-height: 1.65; font-weight: 450; opacity: .9; }
[data-testid="stWidgetLabel"] p, [data-testid="stRadio"] label p { font-weight: 550; line-height: 1.65; }
button p, input, textarea { font-size: 1rem; font-weight: 500; line-height: 1.65; }
.hero { padding: 1rem 0 1.5rem; }
.eyebrow { color: #6750c5; font-size: .95rem; font-weight: 650; letter-spacing: .05em; }
.hero h1 { font-size: clamp(2rem, 5vw, 2.9rem); line-height: 1.2; padding: .7rem 0; }
.subtitle { font-size: 1.14rem; line-height: 1.7; font-weight: 450; }
.pill { display: inline-block; border: 1px solid #8270df66; border-radius: 99px;
        padding: .3rem .7rem; font-size: .9rem; margin-top: .8rem; }
[data-testid="stFileUploaderDropzone"] { border: 1px dashed #8270df88; border-radius: 12px; }
div.stButton > button { min-height: 2.8rem; border-radius: 10px; }
div.stButton > button[kind="primary"] { background: #6750c5; color: white; border: 1px solid #6750c5; font-weight: 650; }
div.stButton > button[kind="primary"]:hover { background: #5540ae; border-color: #5540ae; }
div[class*="st-key-explain-"] button { min-height: 2rem; padding: .15rem .55rem; opacity: .82; font-size: .92rem; }
.capabilities { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin: .8rem 0 1.2rem; }
.capability { border: 1px solid #8270df33; border-radius: 14px; padding: 1.1rem; background: #8270df08; }
.capability h3 { font-size: 1.08rem; padding: .5rem 0; }
.capability p { font-size: .96rem; line-height: 1.7; margin: 0; }
.symbol { color: #6750c5; font-size: 1.35rem; }
.source { border-color: #8270df88; background: #8270df12; }
.source-note { border-left: 3px solid #8270df; padding: .5rem 1rem; font-size: .96rem; line-height: 1.7; margin: 1rem 0; }
@media (max-width: 640px) {
  .capabilities { grid-template-columns: 1fr; }
  .block-container { padding-top: 1rem; }
}
</style>
"""


def render_header():
    st.markdown(STYLES, unsafe_allow_html=True)
    with st.columns([2, 1])[1]:
        st.selectbox("語言 / Language", options=list(LANGUAGE_NAMES),
                     index=list(LANGUAGE_NAMES).index(current_language()),
                     format_func=LANGUAGE_NAMES.get, key="product_language")
    # These HTML interpolations contain only trusted static translations.
    st.markdown(f"""
    <div class="hero">
      <div class="eyebrow">{tr('See the idea. Find the connection.')}</div>
      <h1>Visual Learning Lab</h1>
      <div class="subtitle">{tr('Turn complex ideas into something you can actually see.')}</div>
      <span class="pill">2026 iThome Ironman · Day 20 / 30</span>
    </div>
    """, unsafe_allow_html=True)


def render_footer():
    st.markdown(f"### {tr('One idea. More ways to understand it.')}")
    st.caption(tr("Planned capabilities · coming in future versions"))
    capabilities = [
        ("≈", "Analogies", "Make unfamiliar ideas click with familiar examples."),
        ("▧", "Image Breakdown", "Explore the parts of a diagram and what they mean."),
        ("◇", "Richer 3D experiences", "Explore spatial models beyond point trajectories."),
        ("↗", "Source Check", "Trace explanations back to the original PDF or source material."),
    ]
    cards = "".join(
        f'<article class="capability {"source" if title == "Source Check" else ""}">'
        f'<span class="symbol" aria-hidden="true">{symbol}</span>'
        f'<h3>{tr(title)}</h3><p>{tr(description)}</p></article>'
        for symbol, title, description in capabilities
    )
    st.markdown(f'<div class="capabilities">{cards}</div>', unsafe_allow_html=True)
    st.markdown(f"""<div class="source-note"><strong>{tr('Understanding should come with evidence.')}</strong><br>
    {tr('Planned Source Check will link generated explanations to their supporting source passages, so you can inspect the original context and spot oversimplifications.')}</div>""", unsafe_allow_html=True)
    st.divider()
    st.caption(tr("Visual Learning Lab · Built in public, one day at a time."))

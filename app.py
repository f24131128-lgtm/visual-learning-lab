"""Visual Learning Lab — Day 2 UI prototype. Run with streamlit run app.py."""

import streamlit as st

st.set_page_config(page_title="Visual Learning Lab", page_icon="✦", layout="centered")

# Static presentation styles only; content inputs are never inserted into HTML.
st.markdown("""
<style>
.block-container { max-width: 980px; padding-top: 3rem; padding-bottom: 3rem; }
.hero { padding: 2rem 0 1.5rem; }
.eyebrow { color: #8270df; font-size: .76rem; font-weight: 700;
           letter-spacing: .15em; text-transform: uppercase; }
.hero h1 { font-size: clamp(2.3rem, 6vw, 3.7rem); line-height: 1.12;
           letter-spacing: -.055em; padding: .7rem 0; }
.subtitle { font-size: 1.15rem; opacity: .75; line-height: 1.65; }
.pill { display: inline-block; border: 1px solid #8270df66; border-radius: 99px;
        padding: .3rem .7rem; font-size: .75rem; margin-top: .8rem; }
[data-testid="stFileUploaderDropzone"] { border: 1px dashed #8270df88;
                                         border-radius: 12px; }
div.stButton > button[kind="primary"] { background: #6750c5; color: white;
    border: 1px solid #6750c5; border-radius: 10px; min-height: 3rem;
    font-weight: 650; }
div.stButton > button[kind="primary"]:hover { background: #5540ae;
                                            border-color: #5540ae; }
.capabilities { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 12px; margin: .8rem 0 1.2rem; }
.capability { border: 1px solid #8270df33; border-radius: 14px;
              padding: 1.1rem; background: #8270df08; }
.capability h3 { font-size: 1rem; padding: .5rem 0; }
.capability p { font-size: .86rem; line-height: 1.55; opacity: .75; margin: 0; }
.symbol { color: #8270df; font-size: 1.35rem; }
.source { border-color: #8270df88; background: #8270df12; }
.source-note { border-left: 3px solid #8270df; padding: .5rem 1rem;
               font-size: .9rem; line-height: 1.6; margin: 1rem 0; }
@media (max-width: 640px) {
    .capabilities { grid-template-columns: 1fr; }
    .block-container { padding-top: 1.5rem; }
}
</style>
<div class="hero">
    <div class="eyebrow">See the idea. Find the connection.</div>
    <h1>Visual Learning Lab</h1>
    <div class="subtitle">Turn complex ideas into something you can actually see.</div>
    <span class="pill">2026 iThome Ironman · Day 2 prototype</span>
</div>
""", unsafe_allow_html=True)

with st.container(border=True):
    st.subheader("Start with what you’re learning")
    st.caption("Bring a page, a chapter, or an idea you want to understand.")
    st.file_uploader("Upload a PDF", type=["pdf"],
                     help="Day 2 preview: files can be selected but are not processed.")
    st.text_area("Or paste your content", height=200,
                 placeholder="Paste your notes, a tricky explanation, or a concept you want to explore…")
    st.caption("UI preview only · PDF processing and visualization generation are coming later.")
    if st.button("Visualize", type="primary", use_container_width=True):
        st.info("Visualization generation will be added in a future version.")

st.markdown("### One idea. More ways to understand it.")
st.caption("Planned capabilities · coming in future versions")

capabilities = [
    ("◎", "Concept Map", "Connect key ideas and see how they relate."),
    ("→", "Flow", "Follow a process, one clear step at a time."),
    ("≈", "Analogies", "Make unfamiliar ideas click with familiar examples."),
    ("▧", "Image Breakdown", "Explore the parts of a diagram and what they mean."),
    ("◇", "3D / Motion", "Explore spatial ideas and how systems change."),
    ("↗", "Source Check", "Trace explanations back to the original PDF or source material."),
]

cards = "".join(
    f'<article class="capability {"source" if title == "Source Check" else ""}">'
    f'<span class="symbol" aria-hidden="true">{symbol}</span>'
    f'<h3>{title}</h3><p>{description}</p></article>'
    for symbol, title, description in capabilities
)
st.markdown(f'<div class="capabilities">{cards}</div>', unsafe_allow_html=True)
st.markdown("""
<div class="source-note"><strong>Understanding should come with evidence.</strong><br>
Planned Source Check will link generated explanations to their supporting source passages,
so you can inspect the original context and spot oversimplifications.</div>
""", unsafe_allow_html=True)
st.divider()
st.caption("Visual Learning Lab · Built in public, one day at a time.")

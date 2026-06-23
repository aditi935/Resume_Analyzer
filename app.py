"""
app.py  –  ATS Resume Analyzer  |  Streamlit Frontend
Run with:  streamlit run app.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import time
import os
from dotenv import load_dotenv

load_dotenv()  # loads OPENAI_API_KEY from .env into environment

# ── Local logic module ────────────────────────────────────────────────────────
from resume_logic import run_ats_analysis
# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG  &  CUSTOM CSS
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="ATS Resume Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ===== Icons =====
AI_ICON = "💡"    
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,400&display=swap');

/* ── Root palette ── */
:root {
    --bg:        #0d0f14;
    --surface:   #161921;
    --card:      #1c2030;
    --border:    #2a2f42;
    --accent:    #6c63ff;
    --accent2:   #00d4aa;
    --accent3:   #ff6b6b;
    --text:      #e8eaf2;
    --muted:     #8b91a8;
    --green:     #22c55e;
    --yellow:    #eab308;
    --orange:    #f97316;
    --red:       #ef4444;
}

/* ── Global reset ── */
html, body, [class*="css"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

/* ── Headers ── */
h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    color: var(--text) !important;
}

/* ── Score card ── */
.score-card {
    background: linear-gradient(135deg, var(--card) 0%, #232840 100%);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.score-card::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at center, rgba(108,99,255,0.08) 0%, transparent 60%);
}
.score-number {
    font-family: 'Syne', sans-serif;
    font-size: 5rem;
    font-weight: 800;
    line-height: 1;
    margin: 0.5rem 0;
}
.score-label {
    font-size: 1.1rem;
    color: var(--muted);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    font-weight: 500;
}
.score-rating {
    display: inline-block;
    padding: 0.3rem 1.2rem;
    border-radius: 50px;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.9rem;
    margin-top: 0.75rem;
    letter-spacing: 0.05em;
}

/* ── Metric cards ── */
.metric-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.5rem;
}
.metric-title {
    font-size: 0.78rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.4rem;
    font-weight: 500;
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    line-height: 1.1;
}

/* ── Keyword chips ── */
.chip-container { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.5rem; }
.chip {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 50px;
    font-size: 0.78rem;
    font-weight: 500;
    font-family: 'DM Sans', sans-serif;
}
.chip-green  { background: rgba(34,197,94,0.15);  color: var(--green);  border: 1px solid rgba(34,197,94,0.3);  }
.chip-red    { background: rgba(239,68,68,0.15);   color: var(--red);    border: 1px solid rgba(239,68,68,0.3);   }
.chip-purple { background: rgba(108,99,255,0.15);  color: var(--accent); border: 1px solid rgba(108,99,255,0.3);  }

/* ── Section badge ── */
.section-badge {
    display: inline-flex; align-items: center; gap: 0.4rem;
    padding: 0.3rem 0.9rem;
    border-radius: 8px;
    font-size: 0.82rem;
    font-weight: 500;
    margin: 0.2rem;
}
.badge-found   { background: rgba(34,197,94,0.12);  color: var(--green); border: 1px solid rgba(34,197,94,0.25); }
.badge-missing { background: rgba(239,68,68,0.12);  color: var(--red);   border: 1px solid rgba(239,68,68,0.25); }

/* ── Feedback box ── */
.feedback-box {
    background: var(--card);
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent);
    border-radius: 12px;
    padding: 1.5rem;
    line-height: 1.75;
}

/* ── Upload area ── */
[data-testid="stFileUploader"] {
    border: 2px dashed var(--border) !important;
    border-radius: 14px !important;
    background: var(--card) !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent) 0%, #8b85ff 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.65rem 2rem !important;
    width: 100% !important;
    letter-spacing: 0.05em !important;
    transition: opacity 0.2s, transform 0.15s !important;
    box-shadow: 0 4px 20px rgba(108,99,255,0.35) !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] button {
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    color: var(--muted) !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
}

/* ── Progress bars ── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, var(--accent) 0%, var(--accent2) 100%) !important;
    border-radius: 4px !important;
}

/* ── Text area / input ── */
textarea, .stTextArea textarea {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

/* ── Alerts ── */
.stAlert { border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def colour_for_score(score: float) -> str:
    if score >= 80: return "#22c55e"
    if score >= 60: return "#f97316"
    if score >= 40: return "#eab308"
    return "#ef4444"

def badge_colour(score: float) -> str:
    if score >= 80: return "background:rgba(34,197,94,0.18);color:#22c55e;border:1px solid rgba(34,197,94,0.4)"
    if score >= 60: return "background:rgba(249,115,22,0.18);color:#f97316;border:1px solid rgba(249,115,22,0.4)"
    if score >= 40: return "background:rgba(234,179,8,0.18);color:#eab308;border:1px solid rgba(234,179,8,0.4)"
    return "background:rgba(239,68,68,0.18);color:#ef4444;border:1px solid rgba(239,68,68,0.4)"

def render_chips(items: list, chip_class: str):
    html = '<div class="chip-container">'
    for item in items:
        html += f'<span class="chip {chip_class}">{item}</span>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def gauge_chart(score: float, title: str, height: int = 220):
    colour = colour_for_score(score)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "%", "font": {"size": 28, "color": colour, "family": "Syne"}},
        gauge={
            "axis": {"range": [0, 100], "tickfont": {"color": "#8b91a8", "size": 10}},
            "bar":  {"color": colour, "thickness": 0.35},
            "bgcolor": "#1c2030",
            "bordercolor": "#2a2f42",
            "steps": [
                {"range": [0, 40],  "color": "rgba(239,68,68,0.1)"},
                {"range": [40, 60], "color": "rgba(234,179,8,0.1)"},
                {"range": [60, 80], "color": "rgba(249,115,22,0.1)"},
                {"range": [80,100], "color": "rgba(34,197,94,0.1)"},
            ],
            "threshold": {"line": {"color": colour, "width": 3}, "thickness": 0.75, "value": score},
        },
        title={"text": title, "font": {"color": "#8b91a8", "size": 11, "family": "DM Sans"}},
    ))
    fig.update_layout(
        height=height, margin=dict(l=20, r=20, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e8eaf2",
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1rem 0 1.5rem'>
        <div style='font-family:Syne,sans-serif;font-size:1.6rem;font-weight:800;
                    background:linear-gradient(135deg,#6c63ff,#00d4aa);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
                     ATS Analyzer
        </div>
        <div style='color:#8b91a8;font-size:0.82rem;margin-top:0.3rem;letter-spacing:0.08em;'>
            AI-Powered Resume Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div style='color:#8b91a8;font-size:0.78rem;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.6rem;font-weight:500'>Upload Resume</div>", unsafe_allow_html=True)

    resume_file = st.file_uploader(
        label="", type=["pdf", "docx"],                 
        label_visibility="collapsed",
        key="resume_upload",
    )

    st.markdown("<div style='margin-top:1rem;color:#8b91a8;font-size:0.78rem;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.6rem;font-weight:500'>Job Description</div>", unsafe_allow_html=True)

    jd_text = st.text_area(
        label="",
        placeholder="Paste the job description here...\n\nTip: Include the full JD for best results.",
        height=220,
        label_visibility="collapsed",
        key="jd_input",
    )

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

    use_llm = st.toggle(
    f"{AI_ICON} AI-Powered Suggestions",
    value=True,
    help="Uses OpenAI GPT-4o to generate personalised improvement tips (requires OPENAI_API_KEY in environment)"
)
    st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)

    analyse_btn = st.button("🚀 Analyse Resume", use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <div style='color:#8b91a8;font-size:0.75rem;line-height:1.7;'>
    <strong style='color:#6c63ff'>How it works:</strong><br>
    1. Upload your resume (PDF/DOCX)<br>
    2. Paste the job description<br>
    3. Click Analyse<br>
    4. Get your ATS score + AI tips
    <br><br>
    <strong style='color:#6c63ff'>Scoring weights:</strong><br>
    • Keywords → 40%<br>
    • Section check → 30%<br>
    • Skill coverage → 30%
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN AREA
# ══════════════════════════════════════════════════════════════════════════════

# ── Hero header ──────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding:2rem 0 1rem;'>
    <h1 style='font-family:Syne,sans-serif;font-size:2.4rem;font-weight:800;margin:0;'>
        <span style='background:linear-gradient(135deg,#6c63ff,#00d4aa);
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
            ATS Resume Analyzer
        </span>
    </h1>
    <p style='color:#8b91a8;margin-top:0.4rem;font-size:1rem;'>
        Upload your resume and job description to receive an instant ATS compatibility score,
        keyword analysis, skill gap detection, and AI-powered improvement suggestions.
    </p>
</div>
""", unsafe_allow_html=True)

# ── State ────────────────────────────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state.results = None

# ── Landing state ─────────────────────────────────────────────────────────────
if not analyse_btn and st.session_state.results is None:
    st.markdown("""
    <div style='background:rgba(108,99,255,0.06);border:1px solid rgba(108,99,255,0.2);
                border-radius:16px;padding:3rem 2rem;text-align:center;margin-top:2rem;'>
        <div style='font-size:3.5rem;margin-bottom:1rem;'>📄</div>
        <div style='font-family:Syne,sans-serif;font-size:1.3rem;font-weight:700;margin-bottom:0.5rem;'>
            Ready to Analyze Your Resume?
        </div>
        <div style='color:#8b91a8;max-width:440px;margin:0 auto;line-height:1.7;'>
            Upload your resume and paste the job description in the sidebar, then hit <strong style='color:#6c63ff'>Analyse Resume</strong>.
            Your results will appear here in seconds.
        </div>
        <div style='margin-top:2rem;display:flex;justify-content:center;gap:2rem;flex-wrap:wrap;'>
            <div style='color:#8b91a8;font-size:0.85rem;'><span style='color:#6c63ff'>✓</span> PDF / DOCX / TXT</div>
            <div style='color:#8b91a8;font-size:0.85rem;'><span style='color:#00d4aa'>✓</span> Instant scoring</div>
            <div style='color:#8b91a8;font-size:0.85rem;'><span style='color:#ff6b6b'>✓</span> AI suggestions</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Analysis trigger ──────────────────────────────────────────────────────────
if analyse_btn:
    if not resume_file:
        st.error("⚠️ Please upload your resume from the sidebar.")
    elif not jd_text.strip():
        st.error("⚠️ Please paste the job description in the sidebar.")
    else:
        with st.spinner("🔍 Analysing your resume..."):
            progress = st.progress(0, text="Extracting text…")
            time.sleep(0.3)
            progress.progress(20, text="Matching keywords…")
            time.sleep(0.2)
            progress.progress(40, text="Scoring sections…")
            time.sleep(0.2)
            progress.progress(60, text="Detecting skill gaps…")

            try:
                results = run_ats_analysis(resume_file, jd_text, generate_feedback=use_llm)
                st.session_state.results = results
                progress.progress(100, text="Done!")
                time.sleep(0.4)
                progress.empty()
                st.success("✅ Analysis complete!")
            except Exception as e:
                progress.empty()
                st.error(f"❌ Error during analysis: {e}")
                st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# RESULTS DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

if st.session_state.results:
    R   = st.session_state.results
    ats = R["ats"]
    kw  = R["keywords"]
    sec = R["sections"]
    sg  = R["skill_gaps"]
    llm = R["llm_feedback"]

    colour  = colour_for_score(ats["ats_score"])
    bstyle  = badge_colour(ats["ats_score"])

    # ── Row 1: Big Score Card + Metric Cards ─────────────────────────────────
    c1, c3 = st.columns([1.2, 1.4])

    with c1:
        st.markdown(f"""
        <div class="score-card">
            <div class="score-label">ATS Score</div>
            <div class="score-number" style="color:{colour};">{ats['ats_score']}</div>
            <div style="color:#8b91a8;font-size:0.85rem;">out of 100</div>
            <div class="score-rating" style="{bstyle}">{ats['rating']}</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        def mini_metric(title, value, icon):
            c = colour_for_score(value)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">{icon} {title}</div>
                <div class="metric-value" style="color:{c};">{value}%</div>
                <div style="background:#2a2f42;border-radius:4px;height:6px;margin-top:0.5rem;">
                    <div style="width:{value}%;background:{c};height:6px;border-radius:4px;transition:width 0.6s;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        mini_metric("Keyword Match",   ats["keyword_score"],   "🔑")
        mini_metric("Section Score",   ats["section_score"],   "📋")
        mini_metric("Skill Coverage",  ats["skill_gap_score"], "🛠")

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs([
        "🔑 Keywords", "📋 Sections", "💡 AI Feedback"
    ])

    # ── TAB 1: Keywords ───────────────────────────────────────────────────────
    with tab1:
        st.markdown("### Keyword Analysis")

        col_a, col_b = st.columns(2)
        with col_a:
            st.plotly_chart(gauge_chart(kw["match_score"], "Keyword Match Rate"), use_container_width=True, config={"displayModeBar": False})

        with col_b:
            matched_c = len(kw["matched"])
            missing_c = len(kw["missing"])
            total_c   = matched_c + missing_c
            fig_bar = go.Figure(data=[
                go.Bar(name="Matched", x=["Keywords"], y=[matched_c], marker_color="#22c55e",
                       text=[matched_c], textposition="auto"),
                go.Bar(name="Missing", x=["Keywords"], y=[missing_c], marker_color="#ef4444",
                       text=[missing_c], textposition="auto"),
            ])
            fig_bar.update_layout(
                barmode="group", height=220,
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(font=dict(color="#8b91a8")),
                yaxis=dict(gridcolor="#2a2f42", color="#8b91a8"),
                xaxis=dict(gridcolor="#2a2f42", color="#8b91a8"),
                font_color="#e8eaf2",
                margin=dict(l=10, r=10, t=30, b=10),
                title=dict(text="Match vs Missing", font=dict(color="#8b91a8", size=11)),
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

        c_m, c_n = st.columns(2)
        with c_m:
            st.markdown(f"**✅ Matched Keywords** ({len(kw['matched'])})")
            render_chips(kw["matched"][:30], "chip-green")
        with c_n:
            st.markdown(f"**❌ Missing Keywords** ({len(kw['missing'])})")
            if kw["missing"]:
                render_chips(kw["missing"][:30], "chip-red")
            else:
                st.success("Great! No major keywords are missing.")

        if kw["extra"]:
            with st.expander("🔍 Extra keywords in your resume (not in JD)"):
                render_chips(kw["extra"][:30], "chip-purple")

    # ── TAB 2: Sections ───────────────────────────────────────────────────────
    with tab2:
        st.markdown("### Section Completeness")

        col_left, col_right = st.columns([1, 2])
        with col_left:
            st.plotly_chart(gauge_chart(sec["section_score"], "Section Score"), use_container_width=True, config={"displayModeBar": False})

        with col_right:
            st.markdown("**Section Detection Results**")
            for section, present in sec["details"].items():
                icon   = "✅" if present else "❌"
                cls    = "badge-found" if present else "badge-missing"
                status = "Present" if present else "Missing"
                st.markdown(f'<span class="section-badge {cls}">{icon} {section} — {status}</span>', unsafe_allow_html=True)

        if sec["missing"]:
            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            st.warning(f"**Missing sections:** {', '.join(sec['missing'])}. Adding these sections can significantly improve your ATS score.")

    # # ── TAB 3: Skill Gaps ─────────────────────────────────────────────────────
    # with tab3:
    #     st.markdown("### Skill Gap Analysis")

    #     categories = {k: v for k, v in sg.items() if isinstance(v, dict)}

    #     if not categories:
    #         st.info("No specific skill categories were found in the job description.")
    #     else:
    #         # Summary bar chart
    #         chart_data = []
    #         for cat, data in categories.items():
    #             req  = len(data["required_by_jd"])
    #             have = len(data["present_in_resume"])
    #             chart_data.append({"Category": cat, "Have": have, "Gap": req - have})

    #         df = pd.DataFrame(chart_data)
    #         fig_gap = px.bar(
    #             df, x="Category", y=["Have", "Gap"],
    #             color_discrete_map={"Have": "#22c55e", "Gap": "#ef4444"},
    #             barmode="stack",
    #         )
    #         fig_gap.update_layout(
    #             height=280, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    #             legend=dict(font=dict(color="#8b91a8"), bgcolor="rgba(0,0,0,0)"),
    #             yaxis=dict(gridcolor="#2a2f42", color="#8b91a8"),
    #             xaxis=dict(color="#8b91a8"),
    #             font_color="#e8eaf2",
    #             margin=dict(l=10, r=10, t=20, b=10),
    #         )
    #         st.plotly_chart(fig_gap, use_container_width=True, config={"displayModeBar": False})

    #         # Per-category detail
    #         for cat, data in categories.items():
    #             with st.expander(f"**{cat}** — {len(data['present_in_resume'])}/{len(data['required_by_jd'])} covered"):
    #                 ca, cb = st.columns(2)
    #                 with ca:
    #                     st.markdown("✅ **You have:**")
    #                     render_chips(data["present_in_resume"] or ["—"], "chip-green")
    #                 with cb:
    #                     st.markdown("❌ **You're missing:**")
    #                     render_chips(data["gaps"] or ["None!"], "chip-red")

    # ── TAB 4: AI Feedback ────────────────────────────────────────────────────
    with tab3:
        st.markdown("### 💡 AI-Powered Improvement Plan")

        if not use_llm:
            st.info("Enable **AI-Powered Suggestions** in the sidebar to see personalised feedback.")
        elif llm:
            st.markdown(f'<div class="feedback-box">{llm}</div>', unsafe_allow_html=True)
        else:
            st.warning("AI feedback was not generated. Check that your `OPENAI_API_KEY` environment variable is set.")

    # ── Divider + refresh ─────────────────────────────────────────────────────
    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🔄 Clear & Start Over", key="reset"):
        st.session_state.results = None
        st.rerun()
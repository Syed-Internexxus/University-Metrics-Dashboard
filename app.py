# career_outcomes_dashboard.py
# ------------------------------------------------------------------
#  Streamlit dashboard – Internexxus palette, guaranteed light theme
# ------------------------------------------------------------------
import pandas as pd, numpy as np, streamlit as st
import plotly.express as px, plotly.graph_objects as go
import statsmodels.api as sm
from datetime import datetime

# ───── Brand palette ────────────────────────────────────────────
CLR_MINT   = "#16D5A8"   # primary accent
CLR_SKY_A  = "#C6E5F6"
CLR_SKY_B  = "#C5EBF0"
CLR_SKY_C  = "#D9F8F0"
CLR_SKY_D  = "#BCD9FB"
CLR_TEXT   = "#1F2B46"
CLR_CARD   = "#FFFFFF"
CLR_SHADOW = "rgba(26,39,77,.09)"

# ───── Page meta ───────────────────────────────────────────────
st.set_page_config(page_title="Career Outcomes Dashboard",
                   page_icon="📊",
                   layout="wide",
                   initial_sidebar_state="expanded")

# ───── Global CSS ───────────────────────────────────────────────
st.markdown(
f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
html, body, .stApp, .block-container, .main, 
[data-testid="stAppViewContainer"] {{
    font-family:'Poppins',sans-serif;
    color:{CLR_TEXT};
    background:{CLR_SKY_C};
    background: radial-gradient(ellipse at 25% 15%,
                                {CLR_SKY_C} 0%,
                                {CLR_SKY_B} 35%,
                                {CLR_SKY_D} 70%,
                                {CLR_SKY_A} 100%);
}}
.card {{
    background:{CLR_CARD};
    padding:1.25rem 1.35rem;
    border-radius:14px;
    box-shadow:0 8px 18px {CLR_SHADOW};
    transition:transform .25s;
}}
.card:hover {{ transform:translateY(-4px); }}
.card h3 {{ font-size:1rem; color:{CLR_MINT}; margin:0 0 .25rem 0; letter-spacing:.3px; }}
.card h1 {{ font-size:2.25rem; margin:0; line-height:1.1; }}
.caption  {{ font-size:.78rem; color:#667693; margin-top:.25rem; }}

section[data-testid="stSidebar"] > div:first-child {{
    background:{CLR_CARD};
    border-right:1px solid #E6EEF7;
}}
.stPlotlyChart{{ height:100%; }}
::-webkit-scrollbar        {{ width:8px; }}
::-webkit-scrollbar-thumb  {{ background:{CLR_SKY_D}; border-radius:8px; }}
</style>
""",
unsafe_allow_html=True)

# ─── Plotly config ─────────────────────────────────────────────
px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = [CLR_MINT, CLR_SKY_D, CLR_SKY_B, "#FFA629"]

# ── Load dataset ────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_df() -> pd.DataFrame:
    df = pd.read_csv("synthetic_career_dashboard_data.csv",
                     parse_dates=["RegisteredDate", "GraduationDate",
                                  "InternshipStartDate", "FullTimePlacementDate"])
    df["GraduationYear"] = df["GraduationDate"].dt.year
    df["RegMonth"] = df["RegisteredDate"].dt.to_period("M").astype(str)
    return df

df = load_df()
maj = sorted(df["Major"].unique())
yrs = sorted(df["GraduationYear"].unique())

# ── Sidebar filters ─────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    majors_f = st.multiselect("Major", maj, maj)
    years_f = st.multiselect("Grad Year", yrs, yrs)

df_f = df[df["Major"].isin(majors_f) & df["GraduationYear"].isin(years_f)]

# ── Axis-friendly KPI helper ────────────────────────────────────
def line_with_axes(data, x, y, title=None, color=CLR_MINT):
    fig = px.line(data, x=x, y=y, title=title)
    fig.update_traces(line=dict(color=color, width=2.5))
    fig.update_layout(margin=dict(l=10, r=10, t=20, b=10),
                      height=110,
                      xaxis_title="Month", yaxis_title=None,
                      xaxis_tickangle=-45,
                      xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    return fig

# ── Table header format ─────────────────────────────────────────
header_fmt = dict(
    fill_color=CLR_MINT,
    font=dict(color="#FFFFFF", size=12, family="Poppins"),
    align="left",
)

# ═════════ TOP KPI ROW ══════════════════════════════════════════
c1, c2, c3, c4 = st.columns(4, gap="large")

with c1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>Students</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1>{df_f.shape[0]}</h1>", unsafe_allow_html=True)
    monthly_regs = df_f.groupby("RegMonth").size().reset_index(name="cnt")
    st.plotly_chart(line_with_axes(monthly_regs, "RegMonth", "cnt"),
                    use_container_width=True)
    st.markdown("<p class='caption'>Monthly registrations</p></div>", unsafe_allow_html=True)

with c2:
    rate = df_f["FullTimePlacement"].mean()
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>FT Placement Rate</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1>{rate:.0%}</h1>", unsafe_allow_html=True)
    rolling = (df_f.set_index("GraduationDate")["FullTimePlacement"]
               .resample("M").mean().rolling(3).mean()
               .dropna().reset_index())
    rolling["Month"] = rolling["GraduationDate"].dt.to_period("M").astype(str)
    st.plotly_chart(line_with_axes(rolling, "Month", "FullTimePlacement", color=CLR_SKY_D),
                    use_container_width=True)
    st.markdown("<p class='caption'>3‑month rolling avg</p></div>", unsafe_allow_html=True)

with c3:
    med_gap = int(df_f["DaysToFullTimeJob"].dropna().median())
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>Median Days‑to‑Job</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1>{med_gap}</h1>", unsafe_allow_html=True)
    gap_hist = (df_f["DaysToFullTimeJob"].dropna()
                .clip(upper=365).value_counts(bins=12)
                .sort_index().reset_index(drop=True).rename("cnt"))
    gap_hist["bin"] = gap_hist.index
    st.plotly_chart(line_with_axes(gap_hist, "bin", "cnt", color="#FFA629"),
                    use_container_width=True)
    st.markdown("<p class='caption'>Distribution (≤ 1 yr)</p></div>", unsafe_allow_html=True)

with c4:
    avg_apps = df_f["ApplicationsSubmitted"].mean()
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>Avg Applications</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1>{avg_apps:.1f}</h1>", unsafe_allow_html=True)
    by_major = df_f.groupby("Major")["ApplicationsSubmitted"].mean().reset_index(name="avg")
    by_major["MajorID"] = by_major.index
    st.plotly_chart(line_with_axes(by_major, "MajorID", "avg", color=CLR_SKY_B),
                    use_container_width=True)
    st.markdown("<p class='caption'>Mean per major</p></div>", unsafe_allow_html=True)

# ═════════ SECOND ROW (OUTCOMES OVER TIME) ═══════════════════════
st.markdown("### 📈 Career Outcomes Over Time")

outcomes = df_f.copy()
outcomes["GradMonth"] = outcomes["GraduationDate"].dt.to_period("M").astype(str)
monthly_outcomes = outcomes.groupby("GradMonth").agg({
    "FullTimePlacement": "mean",
    "InternshipPlacement": "mean"
}).reset_index()

fig_outcome = px.line(monthly_outcomes,
                      x="GradMonth",
                      y=["FullTimePlacement", "InternshipPlacement"],
                      labels={"value": "Placement Rate", "GradMonth": "Grad Month"},
                      color_discrete_map={
                          "FullTimePlacement": CLR_MINT,
                          "InternshipPlacement": CLR_SKY_D,
                      })
fig_outcome.update_layout(height=350,
                          xaxis_tickangle=-45,
                          xaxis=dict(showgrid=False),
                          yaxis=dict(ticksuffix="%"))
st.plotly_chart(fig_outcome, use_container_width=True)

# ═════════ BOTTOM ROW (SUMMARY TABLES) ═══════════════════════════
st.markdown("### 🧮 Summary by Major")

summary = df_f.groupby("Major").agg({
    "FullTimePlacement": "mean",
    "InternshipPlacement": "mean",
    "ApplicationsSubmitted": "mean",
    "DaysToFullTimeJob": "median"
}).round(2).reset_index()

summary.columns = ["Major", "FT Placement Rate", "Intern Placement Rate",
                   "Avg Applications", "Median Days to FT Job"]

table = go.Figure(data=[go.Table(
    header=header_fmt,
    cells=dict(values=[summary[c] for c in summary.columns],
               align="left",
               font=dict(family="Poppins"),
               fill_color="white"))
])
st.plotly_chart(table, use_container_width=True)

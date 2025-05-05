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
CLR_SKY_A  = "#C6E5F6"   # lightest blue
CLR_SKY_B  = "#C5EBF0"   # aqua tint
CLR_SKY_C  = "#D9F8F0"   # very light mint
CLR_SKY_D  = "#BCD9FB"   # lavender/sky
CLR_TEXT   = "#1F2B46"   # default text
CLR_CARD   = "#FFFFFF"   # white tiles
CLR_SHADOW = "rgba(26,39,77,.09)"

# ───── Page meta ───────────────────────────────────────────────
st.set_page_config(page_title="Career Outcomes Dashboard",
                   page_icon="📊",
                   layout="wide",
                   initial_sidebar_state="expanded")

# ───── Global CSS (forces light bg on every container) ─────────
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
.stSidebar header, .stSidebar h1, .stSidebar h2, .stSidebar h3 {{
    color:{CLR_MINT};
}}
.stPlotlyChart{{ height:100%; }}
::-webkit-scrollbar        {{ width:8px; }}
::-webkit-scrollbar-thumb  {{ background:{CLR_SKY_D}; border-radius:8px; }}
</style>
""",
unsafe_allow_html=True)

px.defaults.template                 = "plotly_white"
px.defaults.color_discrete_sequence  = [CLR_MINT, CLR_SKY_D, CLR_SKY_B, "#FFA629"]

@st.cache_data(show_spinner=False)
def load_df() -> pd.DataFrame:
    df = pd.read_csv(
        "synthetic_career_dashboard_data.csv",
        parse_dates=["RegisteredDate", "GraduationDate",
                     "InternshipStartDate", "FullTimePlacementDate"],
    )
    df["GraduationYear"] = df["GraduationDate"].dt.year
    df["RegMonth"]       = df["RegisteredDate"].dt.to_period("M").astype(str)
    return df

df   = load_df()
maj  = sorted(df["Major"].unique())
yrs  = sorted(df["GraduationYear"].unique())

with st.sidebar:
    st.header("Filters")
    majors_f = st.multiselect("Major", maj, maj)
    years_f  = st.multiselect("Grad Year", yrs, yrs)

df_f = df[df["Major"].isin(majors_f) & df["GraduationYear"].isin(years_f)]

def spark(data, y, color=CLR_MINT):
    fig = px.line(data, y=y)
    fig.update_traces(showlegend=False, line=dict(color=color, width=2.5))
    fig.update_layout(margin=dict(l=0,r=0,t=0,b=0),
                      height=110,
                      xaxis_visible=False, yaxis_visible=False)
    return fig

header_fmt = dict(
    fill_color=CLR_MINT,
    font=dict(color="#FFFFFF", size=12, family="Poppins"),
    align="left",
)

c1, c2, c3, c4 = st.columns(4, gap="large")

with c1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>Students</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1>{df_f.shape[0]}</h1>", unsafe_allow_html=True)
    st.plotly_chart(spark(df_f.groupby("RegMonth")
                          .size().reset_index(name="cnt"), "cnt"),
                    use_container_width=True)
    st.markdown("<p class='caption'>Monthly registrations</p></div>",
                unsafe_allow_html=True)

with c2:
    rate = df_f["FullTimePlacement"].mean()
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>FT Placement Rate</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1>{rate:.0%}</h1>", unsafe_allow_html=True)
    rolling = (df_f.set_index("GraduationDate")["FullTimePlacement"]
               .resample("M").mean().rolling(3).mean()
               .dropna().reset_index())
    st.plotly_chart(spark(rolling, "FullTimePlacement", CLR_SKY_D),
                    use_container_width=True)
    st.markdown("<p class='caption'>3‑month rolling avg</p></div>",
                unsafe_allow_html=True)

with c3:
    med_gap = int(df_f["DaysToFullTimeJob"].dropna().median())
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>Median Days‑to‑Job</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1>{med_gap}</h1>", unsafe_allow_html=True)
    gap_hist = (df_f["DaysToFullTimeJob"].dropna()
                .clip(upper=365).value_counts(bins=12)
                .sort_index().reset_index(drop=True).rename("cnt"))
    st.plotly_chart(spark(gap_hist, "cnt", "#FFA629"),
                    use_container_width=True)
    st.markdown("<p class='caption'>Distribution (≤ 1 yr)</p></div>",
                unsafe_allow_html=True)

with c4:
    avg_apps = df_f["ApplicationsSubmitted"].mean()
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>Avg Applications</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1>{avg_apps:.1f}</h1>", unsafe_allow_html=True)
    by_major = (df_f.groupby("Major")["ApplicationsSubmitted"]
                .mean().reset_index(name="avg"))
    st.plotly_chart(spark(by_major, "avg", CLR_SKY_B),
                    use_container_width=True)
    st.markdown("<p class='caption'>Mean per major</p></div>",
                unsafe_allow_html=True)

g1, g2, g3 = st.columns([2.5, 1.8, 1.7], gap="large")

with g1:
    stages = {
        "Registered" : df_f.shape[0],
        "Applicants" : (df_f["ApplicationsSubmitted"] > 0).sum(),
        "Shortlisted": (df_f["ShortlistedCount"]  > 0).sum(),
        "Hired"      : df_f["FullTimePlacement"].sum(),
    }
    funnel = px.area(x=list(stages), y=list(stages.values()))
    funnel.update_traces(marker=dict(color=CLR_MINT), line=dict(width=0))
    funnel.update_layout(height=300, margin=dict(l=0,r=0,t=40,b=20),
                         title="Pipeline Conversion")
    st.plotly_chart(funnel, use_container_width=True)
    with st.expander("ℹ️ How to read"):
        st.write("- **Registered**: total filtered students\n"
                 "- **Applicants**: submitted ≥1 application\n"
                 "- **Shortlisted**: received ≥1 shortlist\n"
                 "- **Hired**: accepted FT offers")

with g2:
    summary = (df_f.groupby("Major")
               .agg(Students=("StudentID","count"),
                    AvgApps=("ApplicationsSubmitted","mean"),
                    InternshipRate=("InternshipPlacement","mean"),
                    FTPlacement=("FullTimePlacement","mean"),
                    MedianGap=("DaysToFullTimeJob","median"))
               .assign(AvgApps=lambda d:d["AvgApps"].round(1),
                       InternshipRate=lambda d:(d["InternshipRate"]*100).round(1),
                       FTPlacement=lambda d:(d["FTPlacement"]*100).round(1))
               .reset_index())
    col_scale = ["#1F7536" if v>=80 else "#5CA02C" if v>=70
                 else "#FFAE42" if v>=60 else "#D64C4C"
                 for v in summary["FTPlacement"]]
    cell_cols = [[CLR_CARD]*len(summary)]*4 + [col_scale] + [[CLR_CARD]*len(summary)]
    tbl = go.Figure(go.Table(header=header_fmt | dict(values=list(summary.columns)),
                             cells=dict(values=[summary[c] for c in summary.columns],
                                        fill_color=cell_cols,
                                        font=dict(color=CLR_TEXT,family="Poppins"),
                                        align="left")))
    tbl.update_layout(height=360, margin=dict(l=0,r=0,t=40,b=20),
                      title="Major Overview")
    st.plotly_chart(tbl, use_container_width=True)

with g3:
    uni = (df.groupby("University")
           .agg(Students=("StudentID","count"),
                Placement=("FullTimePlacement","mean"))
           .assign(Placement=lambda d:(d["Placement"]*100).round(1))
           .sort_values("Placement",ascending=False).head(7).reset_index())
    uni_tbl = go.Figure(go.Table(header=header_fmt | dict(values=list(uni.columns)),
                                 cells=dict(values=[uni[c] for c in uni.columns],
                                            fill_color=[CLR_CARD]*len(uni.columns),
                                            font=dict(color=CLR_TEXT,family="Poppins"),
                                            align="left")))
    uni_tbl.update_layout(height=360, margin=dict(l=0,r=0,t=40,b=20),
                          title="Top Universities")
    st.plotly_chart(uni_tbl, use_container_width=True)

b1, b2, b3 = st.columns([1.4,2.4,2.2], gap="large")

with b1:
    placed = df_f["InternshipPlacement"].sum()
    donut = px.pie(names=["Placed","Not Placed"],
                   values=[placed, df_f.shape[0]-placed],
                   hole=0.55,
                   color_discrete_sequence=[CLR_MINT, CLR_SKY_B])
    donut.update_traces(textinfo="none")
    donut.update_layout(height=310, margin=dict(l=0,r=0,t=40,b=20),
                        title="Internship Outcome")
    st.plotly_chart(donut, use_container_width=True)

with b2:
    reg_by_uni = (df_f.groupby("University")
                  .size().reset_index(name="count")
                  .sort_values("count", ascending=False))
    reg_bar = px.bar(reg_by_uni.head(10), x="count", y="University",
                     orientation="h", color_discrete_sequence=[CLR_SKY_D])
    reg_bar.update_layout(height=310, margin=dict(l=0,r=0,t=40,b=20),
                          title="Top Sources by University",
                          yaxis_categoryorder='total ascending')
    st.plotly_chart(reg_bar, use_container_width=True)

with b3:
    reg_trend = (df_f.groupby("RegMonth")
                 .size().reset_index(name="count"))
    trend = px.area(reg_trend, x="RegMonth", y="count",
                    color_discrete_sequence=[CLR_SKY_B])
    trend.update_layout(height=310, margin=dict(l=0,r=0,t=40,b=20),
                        title="Monthly Registration Trend")
    st.plotly_chart(trend, use_container_width=True)

# ── Footer ─────────────────────────────────────────────────────
st.markdown(
    "<div style='text-align:center;margin-top:25px;color:#6C7DA0'>"
    "© 2025 University Career Insights Dashboard</div>",
    unsafe_allow_html=True)

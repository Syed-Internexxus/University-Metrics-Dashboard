# career_outcomes_dashboard.py
# ------------------------------------------------------------------
#  Streamlit dashboard – minimalist, pro palette for university admins
# ------------------------------------------------------------------
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm

# ────────────────────────────────────────────────────────────────
#  COLOR SYSTEM  ▸ neutral / accent / status
# ────────────────────────────────────────────────────────────────
BG        = "#FAFAFC"      # subtle off‑white background
CARD      = "#FFFFFF"      # cards
TXT_MAIN  = "#111827"      # charcoal
TXT_SUB   = "#6B7280"      # muted gray

ACCENT    = "#2563EB"      # blue  – primary highlights / lines
SUCCESS   = "#059669"      # green – success metrics
WARNING   = "#F59E0B"      # orange – durations / alerts
NEUTRAL   = "#94A3B8"      # secondary

SHADOW    = "0 1px 6px rgba(0,0,0,.06)"

px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = [ACCENT, SUCCESS, WARNING, NEUTRAL]

# ────────────────────────────────────────────────────────────────
#  PAGE CONFIG  &  GLOBAL CSS
# ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Career Outcomes Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

html, body, .stApp {{
    background:{BG};
    font-family:'Inter', sans-serif;
    color:{TXT_MAIN};
}}
.card {{
    background:{CARD};
    padding:1.2rem 1.4rem;
    border-radius:12px;
    box-shadow:{SHADOW};
}}
.card h3 {{
    margin:0 0 .4rem 0;
    font-size:1rem;
    font-weight:600;
    color:{ACCENT};
}}
.card h1 {{
    margin:0;
    font-size:2.4rem;
    line-height:1.15;
}}
.caption {{
    font-size:.8rem;
    color:{TXT_SUB};
    margin-top:.35rem;
}}
/* sidebar */
section[data-testid="stSidebar"] > div:first-child {{
    background:{CARD};
    box-shadow:{SHADOW};
}}
.stPlotlyChart {{ height:100%; }}
</style>
""",
    unsafe_allow_html=True,
)

# ────────────────────────────────────────────────────────────────
#  LOAD DATA
# ────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_df():
    df = pd.read_csv(
        "synthetic_career_dashboard_data.csv",
        parse_dates=[
            "RegisteredDate",
            "GraduationDate",
            "InternshipStartDate",
            "FullTimePlacementDate",
        ],
    )
    df["GraduationYear"] = df["GraduationDate"].dt.year
    df["RegMonth"] = df["RegisteredDate"].dt.to_period("M").astype(str)
    return df


df   = load_df()
maj  = sorted(df["Major"].unique())
yrs  = sorted(df["GraduationYear"].unique())

# ────────────────────────────────────────────────────────────────
#  SIDEBAR FILTERS
# ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    majors_f = st.multiselect("Majors", maj, maj)
    years_f  = st.multiselect("Grad Years", yrs, yrs)

df_f = df[df["Major"].isin(majors_f) & df["GraduationYear"].isin(years_f)]

# ────────────────────────────────────────────────────────────────
#  HELPER PLOTS
# ────────────────────────────────────────────────────────────────
def mini_bar(data, x, y, color=ACCENT):
    fig = px.bar(data, x=x, y=y)
    fig.update_traces(marker_color=color, width=.6)
    fig.update_layout(
        height=110,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(tickfont=dict(color=TXT_SUB), tickangle=-45, title=""),
        yaxis=dict(tickfont=dict(color=TXT_SUB), title=""),
    )
    return fig


def mini_area(data, x, y, color=SUCCESS):
    fig = px.area(data, x=x, y=y)
    fig.update_traces(line=dict(color=color, width=2.5), fillcolor=f"rgba(5,150,105,.15)")
    fig.update_layout(
        height=110,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(tickfont=dict(color=TXT_SUB), tickangle=-45, title=""),
        yaxis=dict(tickfont=dict(color=TXT_SUB), title=""),
    )
    return fig


def sparkline(data, y, color):
    fig = px.line(data, y=y)
    fig.update_traces(line=dict(color=color, width=2.5), showlegend=False)
    fig.update_layout(height=110, margin=dict(l=0, r=0, t=0, b=0), xaxis_visible=False, yaxis_visible=False)
    return fig


header_fmt = dict(
    fill_color=ACCENT,
    font=dict(color="#FFFFFF", size=12),
    align="left",
)

# ═══════════════════ TOP KPI ROW ════════════════════════════════
c1, c2, c3, c4 = st.columns(4, gap="large")

# 1 ▸ Students (bar by month)
with c1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>Students</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1>{df_f.shape[0]}</h1>", unsafe_allow_html=True)
    monthly = df_f.groupby("RegMonth").size().reset_index(name="cnt")
    st.plotly_chart(mini_bar(monthly, "RegMonth", "cnt"), use_container_width=True)
    st.markdown("<p class='caption'>New registrations by month</p></div>", unsafe_allow_html=True)

# 2 ▸ FT placement rate (area, 3‑month centered median instead of rolling avg)
with c2:
    rate_total = df_f["FullTimePlacement"].mean()
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>FT Placement Rate</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1>{rate_total:.0%}</h1>", unsafe_allow_html=True)
    # centered 3‑month median
    mp = (
        df_f.set_index("GraduationDate")["FullTimePlacement"]
        .resample("M")
        .median()
        .rolling(window=3, center=True)
        .median()
        .dropna()
        .reset_index()
    )
    mp["Month"] = mp["GraduationDate"].dt.to_period("M").astype(str)
    st.plotly_chart(mini_area(mp, "Month", "FullTimePlacement"), use_container_width=True)
    st.markdown("<p class='caption'>Centered 3‑month median</p></div>", unsafe_allow_html=True)

# 3 ▸ Median days‑to‑job (sparkline)
with c3:
    med_gap = int(df_f["DaysToFullTimeJob"].dropna().median())
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>Median Days‑to‑Job</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1>{med_gap}</h1>", unsafe_allow_html=True)
    dist = (
        df_f["DaysToFullTimeJob"]
        .dropna()
        .clip(upper=365)
        .value_counts(bins=15)
        .sort_index()
        .reset_index(drop=True)
        .rename("v")
    )
    st.plotly_chart(sparkline(dist, "v", WARNING), use_container_width=True)
    st.markdown("<p class='caption'>≤ 12 month distribution</p></div>", unsafe_allow_html=True)

# 4 ▸ Avg applications (sparkline)
with c4:
    avg_apps = df_f["ApplicationsSubmitted"].mean()
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>Avg Applications</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1>{avg_apps:.1f}</h1>", unsafe_allow_html=True)
    mj = df_f.groupby("Major")["ApplicationsSubmitted"].mean().reset_index(name="v")
    st.plotly_chart(sparkline(mj, "v", NEUTRAL), use_container_width=True)
    st.markdown("<p class='caption'>Per student</p></div>", unsafe_allow_html=True)

# ═══════════════════ SECOND ROW ═════════════════════════════════
g1, g2, g3 = st.columns([2.7, 1.7, 1.6], gap="large")

with g1:
    stages = {
        "Registered": df_f.shape[0],
        "Applicants": (df_f["ApplicationsSubmitted"] > 0).sum(),
        "Shortlisted": (df_f["ShortlistedCount"] > 0).sum(),
        "Hired": df_f["FullTimePlacement"].sum(),
    }
    fun = px.area(x=list(stages), y=list(stages.values()), color_discrete_sequence=[ACCENT])
    fun.update_traces(line=dict(width=0))
    fun.update_layout(height=300, margin=dict(l=0, r=0, t=40, b=20), title="Pipeline Conversion")
    st.plotly_chart(fun, use_container_width=True)

with g2:
    overview = (
        df_f.groupby("Major")
        .agg(
            Students=("StudentID", "count"),
            AvgApps=("ApplicationsSubmitted", "mean"),
            Interns=("InternshipPlacement", "mean"),
            FT=("FullTimePlacement", "mean"),
            MedianGap=("DaysToFullTimeJob", "median"),
        )
        .assign(
            AvgApps=lambda d: d["AvgApps"].round(1),
            Interns=lambda d: (d["Interns"] * 100).round(1),
            FT=lambda d: (d["FT"] * 100).round(1),
        )
        .reset_index()
    )
    ft_colors = [
        SUCCESS if v >= 80 else "#A7F3D0" if v >= 70 else WARNING if v >= 60 else "#FED7AA"
        for v in overview["FT"]
    ]
    cell_colors = [[CARD] * len(overview)] * 4 + [ft_colors] + [[CARD] * len(overview)]
    table = go.Figure(
        go.Table(
            header=header_fmt | dict(values=list(overview.columns)),
            cells=dict(
                values=[overview[c] for c in overview.columns],
                fill_color=cell_colors,
                font=dict(color=TXT_MAIN),
                align="left",
            ),
        )
    )
    table.update_layout(
        height=360, margin=dict(l=0, r=0, t=40, b=20), title="Major Overview"
    )
    st.plotly_chart(table, use_container_width=True)

with g3:
    uni = (
        df.groupby("University")
        .agg(Students=("StudentID", "count"), Placement=("FullTimePlacement", "mean"))
        .assign(Placement=lambda d: (d["Placement"] * 100).round(1))
        .sort_values("Placement", ascending=False)
        .head(7)
        .reset_index()
    )
    uni_tbl = go.Figure(
        go.Table(
            header=header_fmt | dict(values=list(uni.columns)),
            cells=dict(
                values=[uni[c] for c in uni.columns],
                fill_color=[CARD] * len(uni.columns),
                font=dict(color=TXT_MAIN),
                align="left",
            ),
        )
    )
    uni_tbl.update_layout(
        height=360, margin=dict(l=0, r=0, t=40, b=20), title="Top Universities"
    )
    st.plotly_chart(uni_tbl, use_container_width=True)

# ═══════════════════ BOTTOM ROW ════════════════════════════════
b1, b2, b3 = st.columns([1.4, 2.4, 2.2], gap="large")

with b1:
    placed = df_f["InternshipPlacement"].sum()
    donut = px.pie(
        names=["Placed", "Not Placed"],
        values=[placed, df_f.shape[0] - placed],
        hole=0.55,
        color_discrete_sequence=[SUCCESS, NEUTRAL],
    )
    donut.update_traces(textinfo="none")
    donut.update_layout(height=310, margin=dict(l=0, r=0, t=40, b=20), title="Internship Outcome")
    st.plotly_chart(donut, use_container_width=True)

with b2:
    sc = px.scatter(
        df_f,
        x="WorkshopAttendance",
        y="InterviewInvites",
        color="Major",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    reg = sm.OLS(df_f["InterviewInvites"], sm.add_constant(df_f["WorkshopAttendance"])).fit()
    m, b_int = reg.params["WorkshopAttendance"], reg.params["const"]
    xs = np.array([df_f["WorkshopAttendance"].min(), df_f["WorkshopAttendance"].max()])
    sc.add_trace(
        go.Scatter(
            x=xs,
            y=m * xs + b_int,
            mode="lines",
            line=dict(color=ACCENT, width=2),
            name="Trend",
        )
    )
    sc.update_layout(
        height=310, margin=dict(l=0, r=0, t=40, b=20), title="Workshop ➜ Interview ROI"
    )
    st.plotly_chart(sc, use_container_width=True)

with b3:
    box = px.box(
        df_f.dropna(subset=["DaysToFullTimeJob"]),
        x="Major",
        y="DaysToFullTimeJob",
        color="Major",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    box.update_layout(
        height=310,
        margin=dict(l=0, r=0, t=40, b=20),
        title="Days to FT Job by Major",
        yaxis_title="Days",
    )
    st.plotly_chart(box, use_container_width=True)

# ────────────────────────────────────────────────────────────────
#  FOOTER
# ────────────────────────────────────────────────────────────────
st.markdown(
    "<div style='text-align:center;margin-top:25px;color:#9CA3AF'>"
    "© 2025 University Career Insights Dashboard</div>",
    unsafe_allow_html=True,
)

# career_outcomes_dashboard.py
# ------------------------------------------------------------------
#  Streamlit dashboard – clean, modern palette (light theme)
# ------------------------------------------------------------------
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm

# ───── Color palette ─────────────────────────────────────────────
BG_SOFT    = "#F7F9FB"      # app background
TXT_MAIN   = "#2E2E2E"      # default (charcoal)
TXT_SECOND = "#64748B"      # slate for captions/axes

CLR_BLUE   = "#3B82F6"      # primary accent
CLR_GREEN  = "#10B981"      # success
CLR_ORANGE = "#F97316"      # alerts / time-to‑job
CLR_SLATE  = "#64748B"      # secondary

CLR_CARD   = "#FFFFFF"
SHADOW     = "0 2px 8px rgba(0,0,0,.05)"

# ───── Page meta ────────────────────────────────────────────────
st.set_page_config(
    page_title="Career Outcomes Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ───── Global CSS ───────────────────────────────────────────────
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
    
    html, body, .stApp, .block-container {{
        font-family:'Poppins',sans-serif;
        background:{BG_SOFT};
        color:{TXT_MAIN};
    }}

    /* Cards */
    .card {{
        background:{CLR_CARD};
        padding:1.25rem 1.35rem;
        border-radius:12px;
        box-shadow:{SHADOW};
    }}
    .card h3 {{ font-size:1rem; color:{CLR_BLUE}; margin:0 0 .3rem 0; }}
    .card h1 {{ font-size:2.3rem; margin:0; }}

    .caption {{ font-size:.8rem; color:{TXT_SECOND}; margin-top:.3rem; }}

    /* Sidebar */
    section[data-testid="stSidebar"] > div:first-child {{
        background:{CLR_CARD};
        box-shadow:{SHADOW};
    }}

    .stPlotlyChart {{ height:100%; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ───── Plotly defaults ──────────────────────────────────────────
px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = [CLR_BLUE, CLR_GREEN, CLR_ORANGE, CLR_SLATE]

# ───── Load dataset ─────────────────────────────────────────────
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


df  = load_df()
maj = sorted(df["Major"].unique())
yrs = sorted(df["GraduationYear"].unique())

# ───── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    majors_f = st.multiselect("Major", maj, maj)
    years_f  = st.multiselect("Grad Year", yrs, yrs)

df_f = df[df["Major"].isin(majors_f) & df["GraduationYear"].isin(years_f)]

# ───── Helpers ──────────────────────────────────────────────────
def line_axes(data, x, y, color):
    fig = px.line(data, x=x, y=y)
    fig.update_traces(line=dict(color=color, width=2.5), showlegend=False)
    fig.update_layout(
        height=110,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis_title="Month",
        yaxis_title="",
        xaxis_tickangle=-45,
        xaxis=dict(showgrid=False, tickfont=dict(color=TXT_SECOND)),
        yaxis=dict(showgrid=False, tickfont=dict(color=TXT_SECOND)),
    )
    return fig


def spark(data, y, color):
    fig = px.line(data, y=y)
    fig.update_traces(line=dict(color=color, width=2.5), showlegend=False)
    fig.update_layout(
        height=110,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis_visible=False,
        yaxis_visible=False,
    )
    return fig


header_fmt = dict(
    fill_color=CLR_BLUE,
    font=dict(color="#FFFFFF", size=12, family="Poppins"),
    align="left",
)

# ═════════ TOP KPI ══════════════════════════════════════════════
c1, c2, c3, c4 = st.columns(4, gap="large")

with c1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>Students</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1>{df_f.shape[0]}</h1>", unsafe_allow_html=True)
    monthly = df_f.groupby("RegMonth").size().reset_index(name="cnt")
    st.plotly_chart(line_axes(monthly, "RegMonth", "cnt", CLR_BLUE), use_container_width=True)
    st.markdown("<p class='caption'>Monthly registrations</p></div>", unsafe_allow_html=True)

with c2:
    rate = df_f["FullTimePlacement"].mean()
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>FT Placement Rate</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1>{rate:.0%}</h1>", unsafe_allow_html=True)
    roll = (
        df_f.set_index("GraduationDate")["FullTimePlacement"]
        .resample("M").mean().rolling(3).mean().dropna().reset_index()
    )
    roll["Month"] = roll["GraduationDate"].dt.to_period("M").astype(str)
    st.plotly_chart(line_axes(roll, "Month", "FullTimePlacement", CLR_GREEN), use_container_width=True)
    st.markdown("<p class='caption'>3‑month rolling avg</p></div>", unsafe_allow_html=True)

with c3:
    med_gap = int(df_f["DaysToFullTimeJob"].dropna().median())
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>Median Days‑to‑Job</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1>{med_gap}</h1>", unsafe_allow_html=True)
    gap_hist = (
        df_f["DaysToFullTimeJob"]
        .dropna()
        .clip(upper=365)
        .value_counts(bins=12)
        .sort_index()
        .reset_index(drop=True)
        .rename("cnt")
    )
    st.plotly_chart(spark(gap_hist, "cnt", CLR_ORANGE), use_container_width=True)
    st.markdown("<p class='caption'>Distribution ≤ 1 yr</p></div>", unsafe_allow_html=True)

with c4:
    avg_apps = df_f["ApplicationsSubmitted"].mean()
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>Avg Applications</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1>{avg_apps:.1f}</h1>", unsafe_allow_html=True)
    by_major = df_f.groupby("Major")["ApplicationsSubmitted"].mean().reset_index(name="avg")
    st.plotly_chart(spark(by_major, "avg", CLR_SLATE), use_container_width=True)
    st.markdown("<p class='caption'>Mean per major</p></div>", unsafe_allow_html=True)

# ═════════ SECOND ROW ═══════════════════════════════════════════
g1, g2, g3 = st.columns([2.6, 1.8, 1.6], gap="large")

with g1:
    stages = {
        "Registered": df_f.shape[0],
        "Applicants": (df_f["ApplicationsSubmitted"] > 0).sum(),
        "Shortlisted": (df_f["ShortlistedCount"] > 0).sum(),
        "Hired": df_f["FullTimePlacement"].sum(),
    }
    funnel = px.area(x=list(stages), y=list(stages.values()), color_discrete_sequence=[CLR_BLUE])
    funnel.update_traces(line=dict(width=0))
    funnel.update_layout(height=300, margin=dict(l=0, r=0, t=40, b=20), title="Pipeline Conversion")
    st.plotly_chart(funnel, use_container_width=True)

with g2:
    summary = (
        df_f.groupby("Major")
        .agg(
            Students=("StudentID", "count"),
            AvgApps=("ApplicationsSubmitted", "mean"),
            InternshipRate=("InternshipPlacement", "mean"),
            FTPlacement=("FullTimePlacement", "mean"),
            MedianGap=("DaysToFullTimeJob", "median"),
        )
        .assign(
            AvgApps=lambda d: d["AvgApps"].round(1),
            InternshipRate=lambda d: (d["InternshipRate"] * 100).round(1),
            FTPlacement=lambda d: (d["FTPlacement"] * 100).round(1),
        )
        .reset_index()
    )
    ft_color = [
        CLR_GREEN if v >= 80 else "#A7F3D0" if v >= 70 else CLR_ORANGE if v >= 60 else "#FECACA"
        for v in summary["FTPlacement"]
    ]
    cell_cols = [[CLR_CARD] * len(summary)] * 4 + [ft_color] + [[CLR_CARD] * len(summary)]
    tbl = go.Figure(
        go.Table(
            header=header_fmt | dict(values=list(summary.columns)),
            cells=dict(
                values=[summary[c] for c in summary.columns],
                fill_color=cell_cols,
                font=dict(color=TXT_MAIN, family="Poppins"),
                align="left",
            ),
        )
    )
    tbl.update_layout(height=360, margin=dict(l=0, r=0, t=40, b=20), title="Major Overview")
    st.plotly_chart(tbl, use_container_width=True)

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
                fill_color=[CLR_CARD] * len(uni.columns),
                font=dict(color=TXT_MAIN, family="Poppins"),
                align="left",
            ),
        )
    )
    uni_tbl.update_layout(height=360, margin=dict(l=0, r=0, t=40, b=20), title="Top Universities")
    st.plotly_chart(uni_tbl, use_container_width=True)

# ═════════ BOTTOM ROW ═══════════════════════════════════════════
b1, b2, b3 = st.columns([1.4, 2.4, 2.2], gap="large")

with b1:
    placed = df_f["InternshipPlacement"].sum()
    donut = px.pie(
        names=["Placed", "Not Placed"],
        values=[placed, df_f.shape[0] - placed],
        hole=0.55,
        color_discrete_sequence=[CLR_GREEN, CLR_SLATE],
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
            line=dict(color=CLR_ORANGE, width=2),
            name="Trend",
        )
    )
    sc.update_layout(
        height=310, margin=dict(l=0, r=0, t=40, b=20), title="Workshop → Interview ROI"
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

# ───── Footer ───────────────────────────────────────────────────
st.markdown(
    "<div style='text-align:center;margin-top:25px;color:#94A3B8'>"
    "© 2025 University Career Insights Dashboard</div>",
    unsafe_allow_html=True,
)

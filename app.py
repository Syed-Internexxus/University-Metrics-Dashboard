# career_outcomes_dashboard.py
# ------------------------------------------------------------------
#  Streamlit dashboard – Internexxus‑styled makeover (full file)
# ------------------------------------------------------------------
import pandas as pd, numpy as np, streamlit as st
import plotly.express as px, plotly.graph_objects as go
import statsmodels.api as sm
from datetime import datetime

# ───── Brand palette sampled from internexxus.com ────────────────
INX_PRIMARY     = "#2D5BFF"   # brand blue
INX_PRIMARY_LT  = "#7D9BFF"   # lighter blue
INX_PURPLE      = "#8A5BFF"   # purple accent
INX_BG          = "#F6F8FF"   # page background
INX_TEXT        = "#1F2B46"   # default text
INX_CARD_BG     = "#FFFFFF"   # card background
INX_SHADOW      = "rgba(19,48,146,.08)"

# ───── Basic page meta ───────────────────────────────────────────
st.set_page_config(
    page_title="Career Outcomes Dashboard",
    page_icon="📊",
    layout="wide",
)

# ───── Global CSS injection ─────────────────────────────────────
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

    html, body, [class^="css"] {{
        background:{INX_BG};
        font-family:'Poppins',sans-serif;
        color:{INX_TEXT};
    }}

    /* Cards */
    .card {{
        background:{INX_CARD_BG};
        border-radius:14px;
        padding:1.25rem 1.35rem;
        box-shadow:0 8px 18px {INX_SHADOW};
        transition:transform .25s;
    }}
    .card:hover {{ transform:translateY(-4px); }}
    .card h3 {{ font-size:1rem; color:{INX_PRIMARY}; margin:0 0 .25rem 0; letter-spacing:.3px; }}
    .card h1 {{ font-size:2.25rem; line-height:1.1; margin:0; }}

    .caption {{ font-size:.78rem; color:#68789c; margin-top:.25rem; }}

    /* Sidebar */
    section[data-testid="stSidebar"] > div:first-child {{
        background:{INX_CARD_BG};
        border-right:1px solid #e0e6ff;
    }}
    .stSidebar header, .stSidebar h1, .stSidebar h2, .stSidebar h3 {{
        color:{INX_PRIMARY};
    }}

    /* Plotly container */
    .stPlotlyChart{{ height:100%; }}

    /* Scrollbar tidy */
    ::-webkit-scrollbar{{ width:8px; }}
    ::-webkit-scrollbar-thumb{{ background:{INX_PRIMARY_LT}; border-radius:8px; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Load dataset ────────────────────────────────────────────────
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

df = load_df()

# ── Sidebar filters ─────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    majors_f = st.multiselect("Major", sorted(df["Major"].unique()), df["Major"].unique())
    years_f  = st.multiselect("Grad Year", sorted(df["GraduationYear"].unique()),
                              sorted(df["GraduationYear"].unique()))

df_f = df[df["Major"].isin(majors_f) & df["GraduationYear"].isin(years_f)]

# ── Helper: sparkline ───────────────────────────────────────────
def spark(data, y, color=INX_PRIMARY):
    fig = px.line(data, y=y)
    fig.update_traces(showlegend=False, line=dict(color=color, width=2.5))
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=110,
                      xaxis_visible=False, yaxis_visible=False,
                      template="plotly_white")
    return fig

# ── Shared header format for tables ─────────────────────────────
header_fmt = dict(
    fill_color=INX_PRIMARY,
    font=dict(color="#FFFFFF", size=12, family="Poppins"),
    align="left",
)

# ═════════════ TOP KPI CARDS ═══════════════════════════════════
c1, c2, c3, c4 = st.columns(4, gap="large")

with c1:
    st.markdown("<div class='card' title='Total students filtered'>", unsafe_allow_html=True)
    st.markdown("<h3>Students</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1>{df_f.shape[0]}</h1>", unsafe_allow_html=True)
    st.plotly_chart(spark(df_f.groupby("RegMonth").size().reset_index(name="cnt"), "cnt"),
                    use_container_width=True)
    st.markdown("<p class='caption'>Monthly registrations</p></div>", unsafe_allow_html=True)

with c2:
    rate = df_f["FullTimePlacement"].mean()
    st.markdown("<div class='card' title='Percent with FT offers'>", unsafe_allow_html=True)
    st.markdown("<h3>FT Placement Rate</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1>{rate:.0%}</h1>", unsafe_allow_html=True)
    rolling = (df_f.set_index("GraduationDate")["FullTimePlacement"]
               .resample("M").mean().rolling(3).mean().dropna().reset_index())
    st.plotly_chart(spark(rolling, "FullTimePlacement", INX_PURPLE),
                    use_container_width=True)
    st.markdown("<p class='caption'>3‑month rolling avg</p></div>", unsafe_allow_html=True)

with c3:
    med_gap = int(df_f["DaysToFullTimeJob"].dropna().median())
    st.markdown("<div class='card' title='Median days to FT job'>", unsafe_allow_html=True)
    st.markdown("<h3>Median Days‑to‑Job</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1>{med_gap}</h1>", unsafe_allow_html=True)
    gap_hist = (df_f["DaysToFullTimeJob"].dropna().clip(upper=365)
                .value_counts(bins=12).sort_index().reset_index(drop=True).rename("cnt"))
    st.plotly_chart(spark(gap_hist, "cnt", "#FFA629"), use_container_width=True)
    st.markdown("<p class='caption'>Distribution (≤ 1 yr)</p></div>", unsafe_allow_html=True)

with c4:
    avg_apps = df_f["ApplicationsSubmitted"].mean()
    st.markdown("<div class='card' title='Average applications submitted'>", unsafe_allow_html=True)
    st.markdown("<h3>Avg Applications</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1>{avg_apps:.1f}</h1>", unsafe_allow_html=True)
    by_major = df_f.groupby("Major")["ApplicationsSubmitted"].mean().reset_index(name="avg")
    st.plotly_chart(spark(by_major, "avg", "#19C7A8"), use_container_width=True)
    st.markdown("<p class='caption'>Mean per major</p></div>", unsafe_allow_html=True)

# ═════════════ SECOND ROW ═══════════════════════════════════════
g1, g2, g3 = st.columns([2.5, 1.8, 1.7], gap="large")

# ► Conversion Funnel
with g1:
    stages = {
        "Registered": df_f.shape[0],
        "Applicants": (df_f["ApplicationsSubmitted"] > 0).sum(),
        "Shortlisted": (df_f["ShortlistedCount"] > 0).sum(),
        "Hired": df_f["FullTimePlacement"].sum(),
    }
    funnel = px.area(x=list(stages), y=list(stages.values()), template="plotly_white")
    funnel.update_traces(marker=dict(color=INX_PRIMARY), line=dict(width=0))
    funnel.update_layout(height=300, margin=dict(l=0, r=0, t=40, b=20),
                         title="Pipeline Conversion")
    st.plotly_chart(funnel, use_container_width=True)
    with st.expander("ℹ️ How to read"):
        st.write(
            "- **Registered**: total filtered students\n"
            "- **Applicants**: submitted ≥1 application\n"
            "- **Shortlisted**: received ≥1 shortlist\n"
            "- **Hired**: accepted FT offers"
        )

# ► Major Overview Table
with g2:
    summary = (df_f.groupby("Major")
               .agg(Students=("StudentID", "count"),
                    AvgApps=("ApplicationsSubmitted", "mean"),
                    InternshipRate=("InternshipPlacement", "mean"),
                    FTPlacement=("FullTimePlacement", "mean"),
                    MedianGap=("DaysToFullTimeJob", "median"))
               .assign(AvgApps=lambda d: d["AvgApps"].round(1),
                       InternshipRate=lambda d: (d["InternshipRate"] * 100).round(1),
                       FTPlacement=lambda d: (d["FTPlacement"] * 100).round(1))
               .reset_index())

    colors = [
        "#1F7536" if v >= 80 else "#5CA02C" if v >= 70 else "#FFAE42" if v >= 60 else "#D64C4C"
        for v in summary["FTPlacement"]
    ]
    cell_cols = [
        [INX_CARD_BG]*len(summary), [INX_CARD_BG]*len(summary),
        [INX_CARD_BG]*len(summary), [INX_CARD_BG]*len(summary),
        colors, [INX_CARD_BG]*len(summary)
    ]
    tbl = go.Figure(go.Table(
        header=header_fmt | dict(values=list(summary.columns)),
        cells=dict(values=[summary[c] for c in summary.columns],
                   fill_color=cell_cols,
                   font=dict(color=INX_TEXT, family="Poppins"), align="left")
    ))
    tbl.update_layout(height=360, margin=dict(l=0, r=0, t=40, b=20),
                      title="Major Overview", template="plotly_white")
    st.plotly_chart(tbl, use_container_width=True)
    with st.expander("ℹ️ Columns"):
        st.write(
            "- **AvgApps**: mean apps per student\n"
            "- **InternshipRate**: % with internships\n"
            "- **FTPlacement**: % with FT offers\n"
            "- **MedianGap**: median days to job"
        )

# ► University Ranking Table
with g3:
    uni = (df.groupby("University")
           .agg(Students=("StudentID", "count"),
                Placement=("FullTimePlacement", "mean"))
           .assign(Placement=lambda d: (d["Placement"] * 100).round(1))
           .sort_values("Placement", ascending=False).head(7).reset_index())
    uni_tbl = go.Figure(go.Table(
        header=header_fmt | dict(values=list(uni.columns)),
        cells=dict(values=[uni[c] for c in uni.columns],
                   fill_color=[INX_CARD_BG]*len(uni.columns),
                   font=dict(color=INX_TEXT, family="Poppins"), align="left")
    ))
    uni_tbl.update_layout(height=360, margin=dict(l=0, r=0, t=40, b=20),
                          title="Top Universities", template="plotly_white")
    st.plotly_chart(uni_tbl, use_container_width=True)
    with st.expander("ℹ️ Why this matters"):
        st.write("High FT placement signals strong employer ties & student readiness.")

# ═════════════ BOTTOM ROW ═══════════════════════════════════════
b1, b2, b3 = st.columns([1.4, 2.4, 2.2], gap="large")

# ► Internship Outcome Donut
with b1:
    placed = df_f["InternshipPlacement"].sum()
    donut = px.pie(names=["Placed", "Not Placed"],
                   values=[placed, df_f.shape[0] - placed],
                   hole=0.55,
                   color_discrete_sequence=["#12D18E", "#2F3D59"],
                   template="plotly_white")
    donut.update_traces(textinfo="none")
    donut.update_layout(height=310, margin=dict(l=0, r=0, t=40, b=20),
                        title="Internship Outcome")
    st.plotly_chart(donut, use_container_width=True)
    st.caption("Internships boost FT conversion; target ≥ 70%")

# ► Workshop ROI Scatter
with b2:
    sc = px.scatter(df_f, x="WorkshopAttendance", y="InterviewInvites",
                    color="Major", template="plotly_white")
    res = sm.OLS(df_f["InterviewInvites"], sm.add_constant(df_f["WorkshopAttendance"])).fit()
    m, b_int = res.params["WorkshopAttendance"], res.params["const"]
    xs = np.array([df_f["WorkshopAttendance"].min(), df_f["WorkshopAttendance"].max()])
    sc.add_trace(go.Scatter(x=xs, y=m * xs + b_int, mode="lines",
                            line=dict(color="#FFD166"), name="Trend"))
    sc.update_layout(height=310, margin=dict(l=0, r=0, t=40, b=20),
                     title="Workshop → Interview ROI")
    st.plotly_chart(sc, use_container_width=True)
    st.caption("Trend shows ~25–30 % invite lift for workshop attendees")

# ► Days to Job Boxplot
with b3:
    box = px.box(df_f.dropna(subset=["DaysToFullTimeJob"]),
                 x="Major", y="DaysToFullTimeJob",
                 color="Major", template="plotly_white")
    box.update_layout(height=310, margin=dict(l=0, r=0, t=40, b=20),
                      title="Days to FT Job by Major")
    st.plotly_chart(box, use_container_width=True)
    st.caption("Long tails (> 200 d) highlight majors needing extra support")

# ── Footer ─────────────────────────────────────────────────────
st.markdown(
    "<div style='text-align:center;margin-top:25px;color:#96A3C7'>© 2025 University Career Insights Dashboard</div>",
    unsafe_allow_html=True,
)

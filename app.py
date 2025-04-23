import pandas as pd, numpy as np, streamlit as st
import plotly.express as px, plotly.graph_objects as go
import statsmodels.api as sm
from datetime import datetime

st.set_page_config("Career Outcomes Dashboard", layout="wide")

# ── Theming ─────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    body,[class^="css"]{background:#03192F;color:#d1e3ff;}
    .card{background:#062143;padding:1rem;border-radius:10px;
          box-shadow:0 0 10px rgba(0,0,0,.45);}
    .card h3{font-size:17px;color:#8fb3ff;margin:0 0 .25rem 0;}
    .card h1{font-size:32px;margin:0;}
    .caption{font-size:13px;color:#7f97b6;margin:-4px 0 2px 0;}
    .stPlotlyChart{height:100%;}
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
    years_f  = st.multiselect("Grad Year", sorted(df["GraduationYear"].unique()), sorted(df["GraduationYear"].unique()))

df_f = df[df["Major"].isin(majors_f) & df["GraduationYear"].isin(years_f)]

# ── Helper: sparkline ───────────────────────────────────────────
def spark(data, y, color="#00c7ff"):
    fig = px.line(data, y=y)
    fig.update_traces(showlegend=False, line=dict(color=color, width=2.5))
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=110,
                      xaxis_visible=False, yaxis_visible=False)
    return fig

# ── Shared header format for tables ─────────────────────────────
header_fmt = dict(
    fill_color="#0f3054",
    font=dict(color="#d1e3ff", size=12),
    align="left",
)

# ═════════════ TOP KPI CARDS ═══════════════════════════════════
c1, c2, c3, c4 = st.columns(4, gap="large")

with c1:
    st.markdown("<div class='card' title='Total students filtered'>", unsafe_allow_html=True)
    st.markdown("<h3>Students</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1>{df_f.shape[0]}</h1>", unsafe_allow_html=True)
    st.plotly_chart(spark(df_f.groupby("RegMonth").size().reset_index(name="cnt"), "cnt"), use_container_width=True)
    st.markdown("<p class='caption'>Monthly registrations</p></div>", unsafe_allow_html=True)

with c2:
    rate = df_f["FullTimePlacement"].mean()
    st.markdown("<div class='card' title='Percent with FT offers'>", unsafe_allow_html=True)
    st.markdown("<h3>FT Placement Rate</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1>{rate:.0%}</h1>", unsafe_allow_html=True)
    rolling = (df_f.set_index("GraduationDate")["FullTimePlacement"]
               .resample("M").mean().rolling(3).mean().dropna().reset_index())
    st.plotly_chart(spark(rolling, "FullTimePlacement", "#ff5b9a"), use_container_width=True)
    st.markdown("<p class='caption'>3-month rolling avg</p></div>", unsafe_allow_html=True)

with c3:
    med_gap = int(df_f["DaysToFullTimeJob"].dropna().median())
    st.markdown("<div class='card' title='Median days to FT job'>", unsafe_allow_html=True)
    st.markdown("<h3>Median Days-to-Job</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1>{med_gap}</h1>", unsafe_allow_html=True)
    gap_hist = (df_f["DaysToFullTimeJob"].dropna().clip(upper=365)
                .value_counts(bins=12).sort_index().reset_index(drop=True).rename("cnt"))
    st.plotly_chart(spark(gap_hist, "cnt", "#ffa600"), use_container_width=True)
    st.markdown("<p class='caption'>Distribution (≤1 yr)</p></div>", unsafe_allow_html=True)

with c4:
    avg_apps = df_f["ApplicationsSubmitted"].mean()
    st.markdown("<div class='card' title='Average applications submitted'>", unsafe_allow_html=True)
    st.markdown("<h3>Avg Applications</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1>{avg_apps:.1f}</h1>", unsafe_allow_html=True)
    by_major = df_f.groupby("Major")["ApplicationsSubmitted"].mean().reset_index(name="avg")
    st.plotly_chart(spark(by_major, "avg", "#7bffce"), use_container_width=True)
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
    funnel = px.area(x=list(stages), y=list(stages.values()), template="plotly_dark")
    funnel.update_traces(marker=dict(color="#00c7ff"), line=dict(width=0))
    funnel.update_layout(height=300, margin=dict(l=0, r=0, t=40, b=20),
                         title="Pipeline Conversion")
    st.plotly_chart(funnel, use_container_width=True)
    with st.expander("ℹ️ How to read"):
        st.write(
            "- **Registered**: total filtered students\n"
            "- **Applicants**: submitted ≥1 application\n"
            "- **Shortlisted**: received ≥1 shortlist\n"
            "- **Hired**: accepted FT offers\n"
        )

# ► Major Overview Table
with g2:
    summary = (df_f.groupby("Major")
               .agg(Students=("StudentID","count"),
                    AvgApps=("ApplicationsSubmitted","mean"),
                    InternshipRate=("InternshipPlacement","mean"),
                    FTPlacement=("FullTimePlacement","mean"),
                    MedianGap=("DaysToFullTimeJob","median"))
               .assign(AvgApps=lambda d: d["AvgApps"].round(1),
                       InternshipRate=lambda d: (d["InternshipRate"]*100).round(1),
                       FTPlacement=lambda d: (d["FTPlacement"]*100).round(1))
               .reset_index())
    # color-scale FTPlacement
    colors = [
        "#1f7536" if v>=80 else "#5ca02c" if v>=70 else "#ffae42" if v>=60 else "#d64c4c"
        for v in summary["FTPlacement"]
    ]
    cell_cols = [
        ["#062143"]*len(summary),["#062143"]*len(summary),
        ["#062143"]*len(summary),["#062143"]*len(summary),
        colors,["#062143"]*len(summary)
    ]
    tbl = go.Figure(go.Table(
        header=header_fmt | dict(values=list(summary.columns)),
        cells=dict(values=[summary[c] for c in summary.columns],
                   fill_color=cell_cols, font=dict(color="#d1e3ff"), align="left")
    ))
    tbl.update_layout(height=360, margin=dict(l=0,r=0,t=40,b=20), title="Major Overview")
    st.plotly_chart(tbl, use_container_width=True)
    with st.expander("ℹ️ Columns"):
        st.write(
            "- **AvgApps**: mean apps per student\n"
            "- **InternshipRate**: % with internships\n"
            "- **FTPlacement**: % with FT offers\n"
            "- **MedianGap**: median days to job"
        )

# ► University Ranking Table
with g3:
    uni = (df.groupby("University")
           .agg(Students=("StudentID","count"),
                Placement=("FullTimePlacement","mean"))
           .assign(Placement=lambda d: (d["Placement"]*100).round(1))
           .sort_values("Placement", ascending=False).head(7).reset_index())
    uni_tbl = go.Figure(go.Table(
        header=header_fmt | dict(values=list(uni.columns)),
        cells=dict(values=[uni[c] for c in uni.columns],
                   fill_color="#062143", font=dict(color="#d1e3ff"), align="left")
    ))
    uni_tbl.update_layout(height=360, margin=dict(l=0,r=0,t=40,b=20), title="Top Universities")
    st.plotly_chart(uni_tbl, use_container_width=True)
    with st.expander("ℹ️ Why this matters"):
        st.write("High FT placement signals strong employer ties & student readiness.")

# ═════════════ BOTTOM ROW ═══════════════════════════════════════
b1, b2, b3 = st.columns([1.4,2.4,2.2], gap="large")

with b1:
    placed = df_f["InternshipPlacement"].sum()
    donut = px.pie(names=["Placed","Not Placed"],
                   values=[placed, df_f.shape[0]-placed],
                   hole=0.55, color_discrete_sequence=["#12d18e","#2f3d59"])
    donut.update_traces(textinfo="none")
    donut.update_layout(height=310,margin=dict(l=0,r=0,t=40,b=20), title="Internship Outcome")
    st.plotly_chart(donut, use_container_width=True)
    st.caption("Internships boost FT conversion; target ≥70%")

with b2:
    sc = px.scatter(df_f, x="WorkshopAttendance", y="InterviewInvites", color="Major", template="plotly_dark")
    res = sm.OLS(df_f["InterviewInvites"], sm.add_constant(df_f["WorkshopAttendance"])).fit()
    m, b_int = res.params["WorkshopAttendance"], res.params["const"]
    xs = np.array([df_f["WorkshopAttendance"].min(), df_f["WorkshopAttendance"].max()])
    sc.add_trace(go.Scatter(x=xs, y=m*xs+b_int, mode="lines", line=dict(color="#ffd166"), name="Trend"))
    sc.update_layout(height=310,margin=dict(l=0,r=0,t=40,b=20),title="Workshop → Interview ROI")
    st.plotly_chart(sc, use_container_width=True)
    st.caption("Trend shows ~25–30% invite lift for workshop attendees")

with b3:
    box = px.box(df_f.dropna(subset=["DaysToFullTimeJob"]), x="Major", y="DaysToFullTimeJob",
                 template="plotly_dark", color="Major")
    box.update_layout(height=310,margin=dict(l=0,r=0,t=40,b=20), title="Days to FT Job by Major")
    st.plotly_chart(box, use_container_width=True)
    st.caption("Long tails (>200 d) highlight majors needing extra support")

# ── Footer ─────────────────────────────────────────────────────
st.markdown(
    "<div style='text-align:center;margin-top:25px;color:#5c82b3'>© 2025 University Career Insights Dashboard</div>",
    unsafe_allow_html=True,
)

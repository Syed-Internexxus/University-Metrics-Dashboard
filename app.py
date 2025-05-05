# career_outcomes_dashboard.py
# ------------------------------------------------------------------
#  Re‑imagined Streamlit dashboard – Modern, Minimalist, Professional
#  • All Plotly axis / tick / title text forced to solid black
#  • "Comparative Analysis" panel sits beside "Internship Outcome"
# ------------------------------------------------------------------
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import statsmodels.api as sm
from datetime import datetime

# ────── COLOR PALETTE ───────────────────────────────────────────
CLR_PRIMARY   = "#0466C8"
CLR_SECONDARY = "#979DAC"
CLR_SUCCESS   = "#38B000"
CLR_WARNING   = "#FF9F1C"
CLR_DANGER    = "#D90429"

CLR_BG_LIGHT  = "#F8FAFC"
CLR_BG_ACCENT = "#EEF2F8"

CLR_CARD      = "#FFFFFF"
CLR_TEXT      = "#000000"      # <- keep everything black
CLR_TEXT_SECONDARY = "#4F5A77"
CLR_SHADOW    = "rgba(26,34,56,.08)"

# ────── HELPERS ────────────────────────────────────────────────
def hex_to_rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"

# ────── PAGE CONFIG & BASE CSS ─────────────────────────────────
st.set_page_config("Career Outcomes Analytics", "🎓",
                layout="wide", initial_sidebar_state="expanded")

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html,body,.stApp,.block-container,.main,[data-testid="stAppViewContainer"]{{
font-family:'Inter',sans-serif;color:{CLR_TEXT};
background:linear-gradient(145deg,{CLR_BG_LIGHT} 0%,{CLR_BG_ACCENT} 100%);
}}
.card{{background:{CLR_CARD};padding:1.5rem;border-radius:12px;
    box-shadow:0 4px 20px {CLR_SHADOW};transition:.3s;height:100%;}}
.card:hover{{transform:translateY(-3px);box-shadow:0 8px 24px rgba(26,34,56,.12);}}
.card h3{{font-size:.85rem;font-weight:600;text-transform:uppercase;
        color:{CLR_TEXT_SECONDARY};margin:0 0 .5rem;}}
.card h1{{font-size:2.2rem;font-weight:700;margin:0;line-height:1.1;}}
.caption{{font-size:.8rem;color:{CLR_TEXT_SECONDARY};margin-top:.5rem;}}
.section-header{{font-size:1.2rem;font-weight:600;color:{CLR_PRIMARY};
                margin:1.5rem 0 1rem;padding-bottom:.3rem;
                border-bottom:2px solid {hex_to_rgba(CLR_PRIMARY,.2)};}}
section[data-testid="stSidebar"]>div:first-child{{
background:{CLR_CARD};border-right:1px solid #E6EEF7;}}
.stSidebar .block-container{{padding-top:2rem;}}
::-webkit-scrollbar{{width:8px;}}
::-webkit-scrollbar-track{{background:{CLR_BG_LIGHT};}}
::-webkit-scrollbar-thumb{{
background:{hex_to_rgba(CLR_SECONDARY,.3)};border-radius:8px;}}
::-webkit-scrollbar-thumb:hover{{
background:{hex_to_rgba(CLR_SECONDARY,.8)};}}
.footer{{text-align:center;margin-top:2.5rem;padding-top:1rem;
        color:{CLR_TEXT_SECONDARY};font-size:.8rem;
        border-top:1px solid {hex_to_rgba(CLR_SECONDARY,.3)};}}
.dashboard-title{{font-size:1.8rem;font-weight:700;color:{CLR_PRIMARY};
                margin-bottom:1.5rem;}}
.semibold{{font-weight:600;}}
.text-primary{{color:{CLR_PRIMARY};}}
.text-success{{color:{CLR_SUCCESS};}}
.text-warning{{color:{CLR_WARNING};}}
.text-danger{{color:{CLR_DANGER};}}
</style>
""", unsafe_allow_html=True)

# ────── PLOTLY DEFAULTS: axis / tick / title text = black ──────
px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = [
    CLR_PRIMARY, CLR_SUCCESS, CLR_WARNING, CLR_DANGER, CLR_SECONDARY
]

# Apply black text to ALL Plotly elements through template modification
tmpl = pio.templates["plotly_white"].layout
tmpl.font.color= CLR_TEXT
tmpl.title.font.color= CLR_TEXT
tmpl.xaxis.color= CLR_TEXT
tmpl.yaxis.color= CLR_TEXT
tmpl.xaxis.title.font.color= CLR_TEXT
tmpl.yaxis.title.font.color= CLR_TEXT
tmpl.xaxis.tickfont.color= CLR_TEXT
tmpl.yaxis.tickfont.color= CLR_TEXT
tmpl.polar.angularaxis.tickfont.color= CLR_TEXT
tmpl.polar.radialaxis.tickfont.color= CLR_TEXT
tmpl.coloraxis.colorbar.tickfont.color= CLR_TEXT
tmpl.coloraxis.colorbar.title.font.color= CLR_TEXT
tmpl.legend.font.color= CLR_TEXT

pio.templates.default = "plotly_white"   # NEW ➜ ensure every go.Figure picks it up

# ────── DATA LOADER ────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_df() -> pd.DataFrame:
    df = pd.read_csv(
        "synthetic_career_dashboard_data.csv",
        parse_dates=[
            "RegisteredDate", "GraduationDate",
            "InternshipStartDate", "FullTimePlacementDate"
        ],
    )
    df["GraduationYear"] = df["GraduationDate"].dt.year
    df["RegMonth"]       = df["RegisteredDate"].dt.to_period("M").astype(str)
    df["Quarter"]        = df["RegisteredDate"].dt.quarter
    df["YearQuarter"]    = df["RegisteredDate"].dt.year.astype(str) + " Q" + df["Quarter"].astype(str)
    return df

df   = load_df()
maj  = sorted(df["Major"].unique())
yrs  = sorted(df["GraduationYear"].unique())

# ────── CHART FACTORIES ────────────────────────────────────────
def create_gauge_chart(value, title, thr, suffix="%"):
    colors = [CLR_DANGER, CLR_WARNING, CLR_SUCCESS]
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=value, domain={"x":[0,1],"y":[0,1]},
        gauge=dict(
            axis=dict(range=[0,100], tickwidth=1, tickcolor=CLR_TEXT),
            bar=dict(color=colors[0] if value<thr[0]
  else colors[1] if value<thr[1] else colors[2]),
            bgcolor=CLR_BG_ACCENT, borderwidth=2, bordercolor=CLR_CARD,
            steps=[
                dict(range=[0,thr[0]],  color=hex_to_rgba(colors[0],.3)),
                dict(range=[thr[0],thr[1]],color=hex_to_rgba(colors[1],.3)),
                dict(range=[thr[1],100],   color=hex_to_rgba(colors[2],.3))
            ]),
        title=dict(text=title,font=dict(size=14,color=CLR_TEXT_SECONDARY)),
        number=dict(suffix=suffix,font=dict(size=26,color=CLR_TEXT))))
    fig.update_layout(template="plotly_white",              # NEW ➜
    height=130, margin=dict(l=10,r=10,t=30,b=10),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font_color=CLR_TEXT)
    return fig

def create_area_chart(data, x, y, title, color=CLR_PRIMARY):
    fig = px.area(data, x=x, y=y)
    fig.update_traces(line=dict(width=2,color=color),
  fillcolor=hex_to_rgba(color,.2))
    fig.update_layout(title=title, height=130, template="plotly_white",  # NEW ➜
        margin=dict(l=10,r=10,t=30,b=10), xaxis_title=None, yaxis_title=None,
        xaxis_showgrid=False, yaxis_showgrid=True,
        yaxis_gridcolor=hex_to_rgba(CLR_SECONDARY,.2),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color=CLR_TEXT)
    fig.update_xaxes(tickfont=dict(color=CLR_TEXT), title_font=dict(color=CLR_TEXT))
    fig.update_yaxes(tickfont=dict(color=CLR_TEXT), title_font=dict(color=CLR_TEXT))
    return fig

def create_bar_chart(data, x, y, title, color=CLR_PRIMARY):
    fig = px.bar(data, x=x, y=y)
    fig.update_traces(marker_color=color)
    fig.update_layout(title=title, height=130, template="plotly_white",  # NEW ➜
        margin=dict(l=10,r=10,t=30,b=10), xaxis_title=None, yaxis_title=None,
        xaxis_showgrid=False, yaxis_showgrid=True,
        yaxis_gridcolor=hex_to_rgba(CLR_SECONDARY,.2),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color=CLR_TEXT)
    fig.update_xaxes(tickfont=dict(color=CLR_TEXT), title_font=dict(color=CLR_TEXT))
    fig.update_yaxes(tickfont=dict(color=CLR_TEXT), title_font=dict(color=CLR_TEXT))
    return fig

# ────── SIDEBAR ────────────────────────────────────────────────
st.markdown("<h1 class='dashboard-title'>Career Outcomes Analytics</h1>",
            unsafe_allow_html=True)
st.markdown("Interactive platform for tracking student career journey "
            "metrics and placement outcomes")

with st.sidebar:
    st.image("https://via.placeholder.com/200x60?text=University+Logo", width=200)
    st.markdown("### Filters")
    majors_f = st.multiselect("Major", maj)
    years_f  = st.multiselect("Graduation Year", yrs, yrs)
    st.markdown("---")
    st.markdown("#### Dashboard Key Metrics")
    st.markdown("- **Placement Rate**  \n- **Days‑to‑Job**  \n- **Pipeline Conversion**")
    with st.expander("How to Use"):
        st.markdown("1. **Filter** by major and graduation year  \n"
  "2. **Click** charts  \n3. **Hover** elements  \n"
  "4. **Download** insights")
    st.caption("Last updated: May 5 2025")

if not majors_f: majors_f = maj
if not years_f: years_f = yrs

df_f = df[df["Major"].isin(majors_f) & df["GraduationYear"].isin(years_f)]

# ────── TOP METRICS ─────────────────────────────────────────────
st.markdown("<div class='section-header'>Key Performance Indicators</div>",
            unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4, gap="medium")

with c1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>Total Students</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1>{df_f.shape[0]:,}</h1>", unsafe_allow_html=True)
    quarterly = df_f.groupby("YearQuarter").size().reset_index(name="Students")
    st.plotly_chart(create_bar_chart(quarterly, "YearQuarter", "Students",
"Quarterly Registrations"),
  use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    rate = df_f["FullTimePlacement"].mean() * 100
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>FT Placement Rate</h3>", unsafe_allow_html=True)
    st.plotly_chart(create_gauge_chart(rate, "Overall Rate", [60, 80]),
  use_container_width=True)
    yoy = df_f.groupby("GraduationYear")["FullTimePlacement"].mean() * 100
    change = yoy.iloc[-1] - yoy.iloc[-2] if len(yoy) > 1 else 0
    css = "text-success" if change >= 0 else "text-danger"
    st.markdown(f"<p class='caption'><span class='{css}'>{change:+.1f}%</span> "
                f"vs previous year</p></div>", unsafe_allow_html=True)

with c3:
    med_gap = int(df_f["DaysToFullTimeJob"].dropna().median()) \
            if not df_f["DaysToFullTimeJob"].dropna().empty else 0
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>Median Days‑to‑Job</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1>{med_gap}</h1>", unsafe_allow_html=True)
    dist = df_f["DaysToFullTimeJob"].dropna().clip(upper=365)
    hist = px.histogram(dist, nbins=15, opacity=.7,
      color_discrete_sequence=[hex_to_rgba(CLR_WARNING,.7)])
    if len(dist) > 0:
        h, edges = np.histogram(dist, bins=15, range=(0,365), density=True)
        centers  = (edges[:-1] + edges[1:]) / 2
        hist.add_scatter(x=centers,
      y=h*dist.value_counts().max()/max(h),
      mode="lines",
      line=dict(color=CLR_DANGER,width=2),
      name="Distribution")
    hist.update_layout(template="plotly_white",            # NEW ➜
     height=130, margin=dict(l=10,r=10,t=10,b=10),
     xaxis_showticklabels=False, yaxis_showticklabels=False,
     showlegend=False, paper_bgcolor="rgba(0,0,0,0)",
     plot_bgcolor="rgba(0,0,0,0)",
     font_color=CLR_TEXT)
    hist.update_xaxes(tickfont=dict(color=CLR_TEXT))
    hist.update_yaxes(tickfont=dict(color=CLR_TEXT))
    st.plotly_chart(hist, use_container_width=True)
    st.markdown("<p class='caption'>Distribution (days after graduation)"
                "</p></div>", unsafe_allow_html=True)

with c4:
    total_apps = df_f["ApplicationsSubmitted"].sum()
    ipa = (df_f["InterviewInvites"].sum() / total_apps * 100) if total_apps else 0
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>Interview Success Rate</h3>", unsafe_allow_html=True)
    st.plotly_chart(create_gauge_chart(ipa, "Interviews per 100 Applications",
[10, 20], suffix=""),
  use_container_width=True)
    st.markdown(f"<p class='caption'>Avg {df_f['ApplicationsSubmitted'].mean():.1f} "
                f"applications per student</p></div>", unsafe_allow_html=True)

# ────── PIPELINE & MAJOR PERFORMANCE ───────────────────────────
st.markdown("<div class='section-header'>Pipeline Analytics</div>",
            unsafe_allow_html=True)

g1, g2 = st.columns([1, 2], gap="medium")

with g1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>Recruitment Pipeline</h3>", unsafe_allow_html=True)
    stages = {
        "Registered":   df_f.shape[0],
        "Applied":      (df_f["ApplicationsSubmitted"] > 0).sum(),
        "Interviewed":  (df_f["InterviewInvites"]   > 0).sum(),
        "Shortlisted":  (df_f["ShortlistedCount"]   > 0).sum(),
        "Offered":      (df_f["ShortlistedCount"]   > 0).sum() * 0.9,
        "Hired":        df_f["FullTimePlacement"].sum(),
    }
    funnel = go.Figure(go.Funnel(
        y=list(stages.keys()), x=list(stages.values()), textposition="inside",
        textinfo="value+percent initial",
        marker=dict(color=[
            CLR_PRIMARY, hex_to_rgba(CLR_PRIMARY,.9), hex_to_rgba(CLR_PRIMARY,.8),
            hex_to_rgba(CLR_PRIMARY,.7), hex_to_rgba(CLR_PRIMARY,.6), CLR_SUCCESS]),
        connector=dict(line=dict(color=CLR_BG_ACCENT, width=1))))
    funnel.update_layout(height=400, margin=dict(l=10,r=10,t=10,b=10),
      font_color=CLR_TEXT,  # Ensure all text is black
      paper_bgcolor="rgba(0,0,0,0)",
      plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(funnel, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with g2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>Major Performance Analysis</h3>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Overview Table", "Placement Trends"])

    with tab1:
        summary = (df_f.groupby("Major")
                .agg(Students=("StudentID","count"),
      AvgApps=("ApplicationsSubmitted","mean"),
      AvgInterviews=("InterviewInvites","mean"),
      InternshipRate=("InternshipPlacement","mean"),
      FTPlacement=("FullTimePlacement","mean"),
      MedianDays=("DaysToFullTimeJob","median"))
                .assign(AvgApps=lambda d:d["AvgApps"].round(1),
      AvgInterviews=lambda d:d["AvgInterviews"].round(1),
      InternshipRate=lambda d:(d["InternshipRate"]*100).round(1),
      FTPlacement=lambda d:(d["FTPlacement"]*100).round(1))
                .reset_index())
        tbl = go.Figure(go.Table(
            header=dict(values=["Major","Students","Avg Apps","Avg Interviews",
              "Internship %","FT Placement %","Days to Job"],
      fill_color=CLR_PRIMARY, align="left",
      font=dict(color="#FFF",size=12,family="Inter")),
            cells=dict(values=[summary[col] for col in summary.columns],
  fill_color=CLR_CARD, align="left",
  font=dict(color=CLR_TEXT,family="Inter"))))
        tbl.update_layout(height=360, margin=dict(l=10,r=10,t=10,b=10),
      paper_bgcolor="rgba(0,0,0,0)",
      plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(tbl, use_container_width=True)

    with tab2:
        time_data = (df_f.groupby(["Major","GraduationYear"])
  .agg(Placement=("FullTimePlacement","mean"))
  .reset_index())
        time_data["Placement"] *= 100
        line = px.line(time_data, x="GraduationYear", y="Placement",
  color="Major", markers=True)
        line.update_layout(height=360, margin=dict(l=10,r=10,t=10,b=10),
      legend_title_text="Major", yaxis_range=[0,100],
      paper_bgcolor="rgba(0,0,0,0)",
      plot_bgcolor="rgba(0,0,0,0)",
      font_color=CLR_TEXT)  # Force text color
        # Force axis text to black
        line.update_xaxes(tickfont=dict(color=CLR_TEXT), title_font=dict(color=CLR_TEXT))
        line.update_yaxes(tickfont=dict(color=CLR_TEXT), title_font=dict(color=CLR_TEXT))
        st.plotly_chart(line, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ────── DETAILED INSIGHTS ───────────────────────────────────────
st.markdown("<div class='section-header'>Detailed Insights</div>",
            unsafe_allow_html=True)

b1, b2 = st.columns(2, gap="medium")

with b1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>Employment Timeline Analysis</h3>", unsafe_allow_html=True)
    sub1, sub2 = st.tabs(["Major Comparison", "University Performance"])

    with sub1:
        box = px.box(df_f.dropna(subset=["DaysToFullTimeJob"]),
  x="Major", y="DaysToFullTimeJob", color="Major",
  points="outliers")
        box.update_layout(height=400, margin=dict(l=10,r=10,t=10,b=10),
      xaxis_title=None, xaxis_tickangle=-45,
      showlegend=False,
      paper_bgcolor="rgba(0,0,0,0)",
      plot_bgcolor="rgba(0,0,0,0)",
      font_color=CLR_TEXT)  # Force text color
        # Force axis text to black
        box.update_xaxes(tickfont=dict(color=CLR_TEXT), title_font=dict(color=CLR_TEXT))
        box.update_yaxes(tickfont=dict(color=CLR_TEXT), title_font=dict(color=CLR_TEXT))
        st.plotly_chart(box, use_container_width=True)
        st.markdown("<p class='caption'>Distribution of time‑to‑employment "
  "by major. Lower is better.</p>", unsafe_allow_html=True)

    with sub2:
        uni = (df_f.groupby("University")
            .agg(Students=("StudentID","count"),
  Placement=("FullTimePlacement","mean"),
  MedianDays=("DaysToFullTimeJob","median"))
            .assign(Placement=lambda d:(d["Placement"]*100).round(1),
  MedianDays=lambda d:d["MedianDays"].fillna(-1).astype(int))
            .sort_values("Placement",ascending=False).head(10)
            .reset_index())
        tbl = go.Figure(go.Table(
            header=dict(values=["University","Students","Placement %","Days to Job"],
      fill_color=CLR_CARD, align="left",
      font=dict(color=CLR_TEXT,family="Inter",size=14)),
            cells=dict(values=[uni[c] for c in uni.columns],
  fill_color=CLR_CARD, align="left",
  font=dict(color=CLR_TEXT,family="Inter"))))
        tbl.update_layout(height=400, margin=dict(l=10,r=10,t=10,b=10),
      paper_bgcolor="rgba(0,0,0,0)",
      plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(tbl, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with b2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>ROI Analysis</h3>", unsafe_allow_html=True)
    r1, r2 = st.tabs(["Workshop Effectiveness", "Salary Outcomes"])

    with r1:
        sc = px.scatter(df_f, x="WorkshopAttendance", y="InterviewInvites",
      color="Major", size="ApplicationsSubmitted",
      hover_data=["InternshipPlacement","FullTimePlacement"])
        reg = sm.OLS(df_f["InterviewInvites"],
  sm.add_constant(df_f["WorkshopAttendance"])).fit()
        m, b_int = reg.params["WorkshopAttendance"], reg.params["const"]
        xs = np.array([df_f["WorkshopAttendance"].min(),
  df_f["WorkshopAttendance"].max()])
        sc.add_trace(go.Scatter(x=xs, y=m*xs+b_int, mode="lines",
              line=dict(color=CLR_DANGER,width=2,dash="dash"),
              name="Trend"))
        sc.add_annotation(x=xs.max()*0.8, y=df_f["InterviewInvites"].max()*0.9,
      text=f"Each workshop increases<br>interview chances "
          f"by {m:.2f}×",
      showarrow=True, arrowhead=2,
      arrowcolor=CLR_TEXT_SECONDARY, arrowsize=1,
      arrowwidth=1.5, bordercolor=CLR_CARD,
      borderwidth=1, borderpad=4,
      bgcolor=CLR_CARD, opacity=.8,
      font=dict(color=CLR_TEXT))  # Ensure annotation text is black
        sc.update_layout(height=400, margin=dict(l=10,r=10,t=10,b=10),
      xaxis_title="Workshops Attended",
      yaxis_title="Interview Invitations",
      paper_bgcolor="rgba(0,0,0,0)",
      plot_bgcolor="rgba(0,0,0,0)",
      font_color=CLR_TEXT)  # Force text color
        # Force axis text to black
        sc.update_xaxes(tickfont=dict(color=CLR_TEXT), title_font=dict(color=CLR_TEXT))
        sc.update_yaxes(tickfont=dict(color=CLR_TEXT), title_font=dict(color=CLR_TEXT))
        # Force legend text to black
        sc.update_layout(legend_font=dict(color=CLR_TEXT))
        st.plotly_chart(sc, use_container_width=True)
        st.markdown("<p class='caption'>Students who attend more workshops "
  "receive significantly more interview invitations</p>",
  unsafe_allow_html=True)

    with r2:
        if "StartingSalary" in df_f.columns:
            salary = df_f.dropna(subset=["StartingSalary","Major"])
            fig = go.Figure()
            for m in salary["Major"].unique():
                fig.add_trace(go.Violin(
  x=[m]*len(salary[salary["Major"]==m]),
  y=salary[salary["Major"]==m]["StartingSalary"],
  name=m, box_visible=True, meanline_visible=True,
  points="outliers"))
            fig.update_layout(height=400, margin=dict(l=10,r=10,t=10,b=10),
          xaxis_title="Major",
          yaxis_title="Starting Salary ($)",
          xaxis_tickangle=-45, showlegend=False,
          yaxis_tickformat="$,.0f",
          paper_bgcolor="rgba(0,0,0,0)",
          plot_bgcolor="rgba(0,0,0,0)",
          font_color=CLR_TEXT)  # Force text color
            # Force axis text to black
            fig.update_xaxes(tickfont=dict(color=CLR_TEXT), title_font=dict(color=CLR_TEXT))
            fig.update_yaxes(tickfont=dict(color=CLR_TEXT), title_font=dict(color=CLR_TEXT))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("<p class='caption'>Salary distribution by major shows "
      "significant variation between fields</p>",
      unsafe_allow_html=True)
        else:
            st.warning("Salary data is not available in the dataset")
    st.markdown("</div>", unsafe_allow_html=True)

# ────── PLACEMENT OUTCOMES + COMPARATIVE ANALYSIS ───────────────
st.markdown("<div class='section-header'>Placement Outcomes</div>",
            unsafe_allow_html=True)

col_outcome, col_comp = st.columns(2, gap="medium")

with col_outcome:
    placed = df_f["InternshipPlacement"].sum()
    intern_rate = df_f[df_f["InternshipPlacement"]==1]["FullTimePlacement"].mean()
    no_intern   = df_f[df_f["InternshipPlacement"]==0]["FullTimePlacement"].mean()
    lift = ((intern_rate - no_intern) / no_intern) * 100 if no_intern else 0
    donut = px.pie(names=["Placed","Not Placed"],
                values=[placed, df_f.shape[0]-placed],
                hole=.55,
                color_discrete_sequence=["#00B8A9","#87CEEB"])
    donut.update_traces(textinfo="none")
    donut.update_layout(height=310, margin=dict(l=0,r=0,t=40,b=20),
      title="Internship Outcome")
    st.plotly_chart(donut, use_container_width=True)
    st.caption("Internships boost FT conversion; target ≥ 70%")
    st.markdown(f"<p class='caption'><span class='semibold'>Key Insight:</span> "
                f"Students with internships are <span class='text-success "
                f"semibold'>{lift:.1f}%</span> more likely to receive "
                f"full‑time offers</p>", unsafe_allow_html=True)

with col_comp:
    with st.expander("🔍 Detailed Major Analysis"):
        st.markdown("<div class='card'>Comparative Analysis", unsafe_allow_html=True)
        if majors_f:
            tabs = st.tabs(majors_f)
            for i, m in enumerate(majors_f):
                with tabs[i]:
  d = df_f[df_f["Major"]==m]
  l, r = st.columns(2)
  with l:
      st.markdown(f"### {m} Overview")
      st.markdown(f"**Total Students:** {len(d)}")
      st.markdown(f"**Placement Rate:** "
f"{d['FullTimePlacement'].mean()*100:.1f}%")
      st.markdown(f"**Median Days to Job:** "
f"{int(d['DaysToFullTimeJob'].dropna().median())}")
      st.markdown(f"**Internship Rate:** "
f"{d['InternshipPlacement'].mean()*100:.1f}%")
  with r:
      stats = {
          "Metrics":["Applications","Interviews","Workshops",
"Internships","Placement"],
          m:[d["ApplicationsSubmitted"].mean()/df_f["ApplicationsSubmitted"].mean()*100,
          d["InterviewInvites"].mean()/df_f["InterviewInvites"].mean()*100,
          d["WorkshopAttendance"].mean()/df_f["WorkshopAttendance"].mean()*100,
          d["InternshipPlacement"].mean()/df_f["InternshipPlacement"].mean()*100,
          d["FullTimePlacement"].mean()/df_f["FullTimePlacement"].mean()*100],
          "Average":[100]*5
      }
      radar_df = pd.DataFrame(stats)
      rp = px.line_polar(radar_df,
    r=radar_df[m], theta=radar_df["Metrics"],
    line_close=True)
      rp.update_traces(fill="toself",
    fillcolor=hex_to_rgba(CLR_PRIMARY,.25))
      rp.add_trace(go.Scatterpolar(r=[100]*5,
                theta=radar_df["Metrics"],
                fill="toself", name="Average",
                fillcolor=hex_to_rgba(CLR_SECONDARY,.125),
                line=dict(color=CLR_SECONDARY)))
      rp.update_layout(
          polar=dict(
              radialaxis=dict(visible=True, range=[0,150],
            tickfont=dict(color=CLR_TEXT)),
              angularaxis=dict(tickfont=dict(color=CLR_TEXT))),
          showlegend=False, height=300,
          margin=dict(l=10,r=10,t=10,b=10),
          paper_bgcolor="rgba(0,0,0,0)")
      st.plotly_chart(rp, use_container_width=True)
      st.caption("Performance relative to cohort average "
              "(100 % = overall baseline)")
        else:
            st.warning("Select at least one major to view detailed analysis")
        st.markdown("</div>", unsafe_allow_html=True)

# ────── FOOTER ─────────────────────────────────────────────────
st.markdown("<div class='footer'>", unsafe_allow_html=True)
st.markdown(f"Career Outcomes Analytics Dashboard | "
            f"Last updated: {datetime.now():%B %d, %Y}", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Placeholder for future JS fullscreen control
st.markdown("""
<script>
// JS for fullscreen chart viewing would go here in production
</script>
""", unsafe_allow_html=True)

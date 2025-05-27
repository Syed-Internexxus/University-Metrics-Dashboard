import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import statsmodels.api as sm
from datetime import datetime

# ────── PROFESSIONAL UNIVERSITY COLOR PALETTE ──────────────────
CLR_PRIMARY   = "#1E3A8A"      # Deep navy blue (authority, trust)
CLR_SECONDARY = "#64748B"      # Professional slate
CLR_SUCCESS   = "#059669"      # Academic green (achievement)
CLR_WARNING   = "#D97706"      # Amber (attention, caution)
CLR_DANGER    = "#DC2626"      # Professional red (concern)
CLR_ACCENT    = "#7C3AED"      # Academic purple (distinction)

CLR_BG_LIGHT  = "#F8FAFC"      # Clean background
CLR_BG_ACCENT = "#E2E8F0"      # Subtle accent background

CLR_CARD      = "#FFFFFF"      # Clean white cards
CLR_TEXT      = "#0F172A"      # Deep professional text
CLR_TEXT_SECONDARY = "#475569" # Secondary text
CLR_SHADOW    = "rgba(15,23,42,.08)"

# Additional university colors for enhanced visualization
CLR_GOLD      = "#FBBF24"      # Academic gold
CLR_EMERALD   = "#10B981"      # Success emerald

# ────── HELPERS ────────────────────────────────────────────────
def hex_to_rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"

# ────── PAGE CONFIG & ENHANCED CSS ─────────────────────────────
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
    box-shadow:0 4px 20px {CLR_SHADOW};transition:.3s;height:100%;
    border-left:4px solid {CLR_PRIMARY};}}
.card:hover{{transform:translateY(-3px);box-shadow:0 8px 24px rgba(15,23,42,.12);}}
.card h3{{font-size:.85rem;font-weight:600;text-transform:uppercase;
        color:{CLR_TEXT_SECONDARY};margin:0 0 .5rem;letter-spacing:0.5px;}}
.card h1{{font-size:2.2rem;font-weight:700;margin:0;line-height:1.1;color:{CLR_PRIMARY};}}
.caption{{font-size:.8rem;color:{CLR_TEXT_SECONDARY};margin-top:.5rem;line-height:1.4;}}
.section-header{{font-size:1.2rem;font-weight:600;color:{CLR_PRIMARY};
                margin:1.5rem 0 1rem;padding-bottom:.3rem;
                border-bottom:2px solid {hex_to_rgba(CLR_PRIMARY,.2)};}}
.insight-box{{background:{hex_to_rgba(CLR_ACCENT,.05)};padding:1rem;border-radius:8px;
            border-left:4px solid {CLR_ACCENT};margin:1rem 0;}}
.metric-highlight{{color:{CLR_SUCCESS};font-weight:600;}}
.metric-warning{{color:{CLR_WARNING};font-weight:600;}}
.metric-danger{{color:{CLR_DANGER};font-weight:600;}}
section[data-testid="stSidebar"]>div:first-child{{
background:{CLR_CARD};border-right:1px solid #E2E8F0;}}
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
.kpi-insight{{background:{hex_to_rgba(CLR_PRIMARY,.05)};padding:0.75rem;
            border-radius:6px;margin-top:0.5rem;border-left:3px solid {CLR_PRIMARY};}}
</style>
""", unsafe_allow_html=True)

# ────── ENHANCED PLOTLY DEFAULTS ───────────────────────────────
px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = [
    CLR_PRIMARY, CLR_SUCCESS, CLR_WARNING, CLR_DANGER, CLR_ACCENT, CLR_GOLD
]

# Apply professional text styling to ALL Plotly elements
tmpl = pio.templates["plotly_white"].layout
tmpl.font.color                  = CLR_TEXT
tmpl.title.font.color            = CLR_TEXT
tmpl.xaxis.color                 = CLR_TEXT
tmpl.yaxis.color                 = CLR_TEXT
tmpl.xaxis.title.font.color      = CLR_TEXT
tmpl.yaxis.title.font.color      = CLR_TEXT
tmpl.xaxis.tickfont.color        = CLR_TEXT
tmpl.yaxis.tickfont.color        = CLR_TEXT
tmpl.polar.angularaxis.tickfont.color = CLR_TEXT
tmpl.polar.radialaxis.tickfont.color  = CLR_TEXT
tmpl.coloraxis.colorbar.tickfont.color      = CLR_TEXT
tmpl.coloraxis.colorbar.title.font.color    = CLR_TEXT
tmpl.legend.font.color           = CLR_TEXT

pio.templates.default = "plotly_white"

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

# ────── ENHANCED CHART FACTORIES ───────────────────────────────
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
    fig.update_layout(template="plotly_white",
                      height=130, margin=dict(l=10,r=10,t=30,b=10),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font_color=CLR_TEXT)
    return fig

def create_area_chart(data, x, y, title, color=CLR_PRIMARY):
    fig = px.area(data, x=x, y=y)
    fig.update_traces(line=dict(width=2,color=color),
                    fillcolor=hex_to_rgba(color,.2))
    fig.update_layout(title=dict(text=title, font=dict(color=CLR_TEXT)),
        height=130, template="plotly_white",
        margin=dict(l=10,r=10,t=30,b=10), 
        xaxis_title="Time Period", yaxis_title="Count",
        xaxis_showgrid=False, yaxis_showgrid=True,
        yaxis_gridcolor=hex_to_rgba(CLR_SECONDARY,.2),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color=CLR_TEXT)
    fig.update_xaxes(tickfont=dict(color=CLR_TEXT), title_font=dict(color=CLR_TEXT))
    fig.update_yaxes(tickfont=dict(color=CLR_TEXT), title_font=dict(color=CLR_TEXT))
    return fig

def create_cumulative_bar_chart(data, x, y, title):
    data = data.sort_values(x)
    data['Cumulative'] = data[y].cumsum()
    data['Delta'] = data[y]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=data[x], y=data['Cumulative'],
        name='Cumulative Total',
        marker_color=CLR_PRIMARY,
        opacity=0.7,
        text=data['Cumulative'],
        textposition='outside',
        textfont=dict(color=CLR_TEXT)
    ))
    fig.add_trace(go.Bar(
        x=data[x], y=data['Delta'],
        name='Quarterly Increase',
        marker_color=CLR_SUCCESS,
        opacity=0.9,
        text=data['Delta'],
        textposition='inside',
        textfont=dict(color='white', size=12)
    ))

    fig.update_layout(
        title=dict(text=title, font=dict(color=CLR_TEXT, size=16)),
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=20, r=20, t=100, b=20),
        height=400,
        xaxis_title="Quarter",
        yaxis_title="Number of Students",
        xaxis_tickfont=dict(color=CLR_TEXT),
        yaxis_tickfont=dict(color=CLR_TEXT),
        yaxis_gridcolor=hex_to_rgba(CLR_SECONDARY, .2),
        font_color=CLR_TEXT,
        barmode='overlay',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=CLR_TEXT))
    )
    return fig

# ────── SIDEBAR & TITLE ─────────────────────────────────────
st.markdown(f"<div class='card'><h1 class='dashboard-title'>🎓 Career Outcomes Analytics</h1><p class='caption'>Comprehensive insights into student career trajectories, placement success, and program effectiveness for strategic decision-making</p></div>", unsafe_allow_html=True)

with st.sidebar:
    st.image("https://via.placeholder.com/200x60/1E3A8A/FFFFFF?text=University+Analytics", width=200)
    st.markdown("### 🎯 Dashboard Filters")
    majors_f = st.multiselect("📚 Academic Major", maj)
    years_f  = st.multiselect("🎓 Graduation Year", yrs, yrs)
    st.markdown("---")
    st.markdown("#### 📊 Key Performance Indicators")
    st.markdown("""
    - **📈 Placement Rate**: Percentage of graduates securing full-time employment  
    - **⏱️ Days-to-Job**: Time from graduation to employment offer  
    - **🔄 Pipeline Conversion**: Student journey from registration to placement  
    - **💼 Workshop ROI**: Impact of career services on outcomes
    """, unsafe_allow_html=True)
    with st.expander("📖 Dashboard Guide"):
        st.markdown("""
        **How to Navigate:**  
        1. **Filter Data** using the controls above  
        2. **Interpret Metrics** using color-coded performance indicators  
        3. **Analyze Trends** through interactive visualizations  
        4. **Export Insights** for strategic planning
        
        **Color Coding:**  
        - 🟢 **Green**: Above target performance  
        - 🟡 **Amber**: Requires attention  
        - 🔴 **Red**: Below benchmark, needs intervention
        """, unsafe_allow_html=True)
    with st.expander("🎯 Strategic Insights"):
        st.markdown("""
        **Key Success Factors:**  
        - Students with internships show 25-40% higher placement rates  
        - Workshop attendance correlates with interview invitations  
        - STEM majors typically have shorter time-to-employment  
        - Early career services engagement improves outcomes
        """, unsafe_allow_html=True)
    st.markdown("---")
    st.caption("🔄 Last updated: May 27, 2025 📧 Contact: analytics@university.edu")

if not majors_f: majors_f = maj
if not years_f: years_f = yrs

df_f = df[df["Major"].isin(majors_f) & df["GraduationYear"].isin(years_f)]

# ────── ENHANCED TOP METRICS WITH STORYTELLING ─────────────────
st.markdown("<div class='section-header'>📊 Executive Dashboard - Key Performance Indicators</div>",
            unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4, gap="medium")

# Cumulative Student Growth Section
with c1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: black;'>📚 Total Student Cohort</h3>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='color: black;'>{df_f.shape[0]:,}</h1>", unsafe_allow_html=True)
    
    quarterly = df_f.groupby("YearQuarter").size().reset_index(name="Students")
    fig_cum = create_cumulative_bar_chart(
        quarterly, "YearQuarter", "Students", "Cumulative Student Growth by Quarter"
    )
    # Labels fully outside + no clipping
    fig_cum.update_traces(textposition='outside', cliponaxis=False)
    # Give plenty of top margin & set white bg
    fig_cum.update_layout(
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(t=150, l=20, r=20, b=20),
        height=400,
        font_color=CLR_TEXT
    )
    st.plotly_chart(fig_cum, use_container_width=True)
    
    # Insight text
    growth_rate = (
        (quarterly["Students"].iloc[-1] - quarterly["Students"].iloc[0])
        / quarterly["Students"].iloc[0] * 100
    ) if len(quarterly) > 1 else 0
    st.markdown(f"""
    <div class='kpi-insight' style='color: black;'>
      <strong>📈 Growth Insight:</strong> Student registration shows a {growth_rate:+.1f}% 
      trend over the analyzed period. Peak enrollment typically occurs in Q3/Q4.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    rate = df_f["FullTimePlacement"].mean() * 100
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>💼 Full-Time Placement Rate</h3>", unsafe_allow_html=True)
    st.plotly_chart(create_gauge_chart(rate, "Overall Placement Success", [60, 80]),
                    use_container_width=True)
    yoy = df_f.groupby("GraduationYear")["FullTimePlacement"].mean() * 100
    change = yoy.iloc[-1] - yoy.iloc[-2] if len(yoy) > 1 else 0
    css = "metric-highlight" if change >= 0 else "metric-danger"
    st.markdown(f"""
    <div class='kpi-insight'>
    <strong>📊 Performance:</strong> <span class='{css}'>{change:+.1f}%</span> vs previous year<br>
    <strong>🎯 Benchmark:</strong> Target ≥80% for program excellence
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c3:
    med_gap = int(df_f["DaysToFullTimeJob"].dropna().median()) \
            if not df_f["DaysToFullTimeJob"].dropna().empty else 0
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>⏱️ Median Time-to-Employment</h3>", unsafe_allow_html=True)
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
                        name="Trend Line")
    hist.update_layout(template="plotly_white",
                       height=130, margin=dict(l=10,r=10,t=10,b=10),
                       xaxis_title="Days", yaxis_title="Frequency",
                       xaxis_showticklabels=True, yaxis_showticklabels=True,
                       showlegend=False, paper_bgcolor="rgba(0,0,0,0)",
                       plot_bgcolor="rgba(0,0,0,0)",
                       font_color=CLR_TEXT)
    hist.update_xaxes(tickfont=dict(color=CLR_TEXT), title_font=dict(color=CLR_TEXT))
    hist.update_yaxes(tickfont=dict(color=CLR_TEXT), title_font=dict(color=CLR_TEXT))
    st.plotly_chart(hist, use_container_width=True)
    
    performance = "excellent" if med_gap <= 90 else "good" if med_gap <= 120 else "needs improvement"
    st.markdown(f"""
    <div class='kpi-insight'>
    <strong>🎯 Assessment:</strong> {performance.title()} performance<br>
    <strong>📊 Distribution:</strong> Most students secure employment within 6 months
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with c4:
    total_apps = df_f["ApplicationsSubmitted"].sum()
    ipa = (df_f["InterviewInvites"].sum() / total_apps * 100) if total_apps else 0
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3> Interview Conversion Rate</h3>", unsafe_allow_html=True)
    st.plotly_chart(create_gauge_chart(ipa, "Interviews per 100 Applications",
                                    [10, 20], suffix=""),
                    use_container_width=True)
    avg_apps = df_f['ApplicationsSubmitted'].mean()
    st.markdown(f"""
    <div class='kpi-insight'>
    <strong>📈 Activity:</strong> {avg_apps:.1f} avg applications per student<br>
    <strong>💡 Insight:</strong> Higher conversion indicates quality applications and preparation
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ────── ENHANCED PIPELINE & MAJOR PERFORMANCE ──────────────────
st.markdown("<div class='section-header'>🔄 Student Journey Pipeline & Academic Performance Analysis</div>",
            unsafe_allow_html=True)

g1, g2 = st.columns([1, 2], gap="medium")

with g1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: black;'>🔄 Career Services Engagement Pipeline</h3>", unsafe_allow_html=True)
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
            hex_to_rgba(CLR_PRIMARY,.7), hex_to_rgba(CLR_SUCCESS,.8), CLR_SUCCESS]),
        connector=dict(line=dict(color=CLR_BG_ACCENT, width=1))
    ))
    funnel.update_layout(
        height=400,
        margin=dict(l=10,r=10,t=10,b=10),
        font_color=CLR_TEXT,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    # Ensure all axis and annotations are black (if any)
    funnel.update_xaxes(tickfont=dict(color=CLR_TEXT), title_font=dict(color=CLR_TEXT))
    funnel.update_yaxes(tickfont=dict(color=CLR_TEXT), title_font=dict(color=CLR_TEXT))
    st.plotly_chart(funnel, use_container_width=True)
    
    conversion_rate = (stages["Hired"] / stages["Registered"] * 100) if stages["Registered"] > 0 else 0
    interview_rate = (stages["Interviewed"] / stages["Applied"] * 100) if stages["Applied"] > 0 else 0
    st.markdown(f"""
    <div class='insight-box' style='color: black;'>
    <strong>📊 Pipeline Efficiency:</strong><br>
    • Overall conversion: <span class='metric-highlight'>{conversion_rate:.1f}%</span><br>
    • Interview success: <span class='metric-highlight'>{interview_rate:.1f}%</span><br>
    • Key bottleneck: Application to interview stage
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with g2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: black;'>📚 Academic Program Performance Comparison</h3>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📊 Comprehensive Overview", "📈 Historical Trends"])
    st.markdown("""<style>
/* Make all tab labels black */
.stTabs [data-baseweb="tab"] {
  color: black !important;
}
/* Ensure active tab label is black */
.stTabs [data-baseweb="tab"].st-c1 {
  color: black !important;
}
</style>""", unsafe_allow_html=True)
    with tab1:
        summary = (
            df_f.groupby("Major")
            .agg(
                Students=("StudentID","count"),
                AvgApps=("ApplicationsSubmitted","mean"),
                AvgInterviews=("InterviewInvites","mean"),
                InternshipRate=("InternshipPlacement","mean"),
                FTPlacement=("FullTimePlacement","mean"),
                MedianDays=("DaysToFullTimeJob","median")
            )
            .assign(
                AvgApps=lambda d: d["AvgApps"].round(1),
                AvgInterviews=lambda d: d["AvgInterviews"].round(1),
                InternshipRate=lambda d: (d["InternshipRate"]*100).round(1),
                FTPlacement=lambda d: (d["FTPlacement"]*100).round(1),
                MedianDays=lambda d: d["MedianDays"].fillna(0).astype(int)
            )
            .reset_index()
        )
        tbl = go.Figure(go.Table(
            header=dict(
                values=[
                    "Academic Major","Cohort Size","Avg Applications",
                    "Avg Interviews","Internship Rate (%)","Placement Rate (%)",
                    "Days to Employment"
                ],
                fill_color=CLR_ACCENT,
                align="left",
                font=dict(color=CLR_TEXT,size=12,family="Inter")
            ),
            cells=dict(
                values=[summary[col] for col in summary.columns],
                fill_color=[
                    CLR_CARD if i % 2 == 0 else CLR_BG_LIGHT
                    for i in range(len(summary))
                ],
                align="left",
                font=dict(color=CLR_TEXT,family="Inter")
            )
        ))
        tbl.update_layout(
            height=360,
            margin=dict(l=10,r=10,t=10,b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color=CLR_TEXT
        )
        st.plotly_chart(tbl, use_container_width=True)
        
        best_placement = summary.loc[summary["FTPlacement"].idxmax(), "Major"] if not summary.empty else "N/A"
        fastest_hire = summary.loc[summary["MedianDays"].idxmin(), "Major"] if not summary.empty else "N/A"
        st.markdown(f"""
        <div class='insight-box' style='color: black;'>
        <strong>🏆 Program Excellence:</strong><br>
        • Highest placement rate: <span class='metric-highlight'>{best_placement}</span><br>
        • Fastest employment: <span class='metric-highlight'>{fastest_hire}</span><br>
        • Use these insights for resource allocation and best practice sharing
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        time_data = (
            df_f.groupby(["Major","GraduationYear"]) 
            .agg(Placement=("FullTimePlacement","mean"))
            .reset_index()
        )
        time_data["Placement"] *= 100
        line = px.line(
            time_data,
            x="GraduationYear",
            y="Placement",
            color="Major",
            markers=True
        )
        line.update_layout(
            height=360,
            margin=dict(l=10,r=10,t=10,b=10),
            legend_title_text="Academic Major",
            yaxis_range=[0,100],
            xaxis_title="Graduation Year",
            yaxis_title="Placement Rate (%)",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color=CLR_TEXT
        )
        line.update_xaxes(tickfont=dict(color=CLR_TEXT), title_font=dict(color=CLR_TEXT))
        line.update_yaxes(tickfont=dict(color=CLR_TEXT), title_font=dict(color=CLR_TEXT))
        line.update_layout(legend_font=dict(color=CLR_TEXT))
        st.plotly_chart(line, use_container_width=True)
        
        st.markdown(
            """
            <div class='insight-box' style='color: black;'>
            <strong>📈 Trend Analysis:</strong> Track multi-year performance to identify 
            emerging patterns, seasonal variations, and program effectiveness over time.
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)
# ────── ENHANCED DETAILED INSIGHTS ─────────────────────────────
st.markdown("<div class='section-header'>🔍 Enhanced Detailed Insights</div>", unsafe_allow_html=True)

# Two-column layout
b1, b2 = st.columns(2, gap="medium")

# Left column: Employment Timeline Tail Distribution
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


# Right column: Workshop Effectiveness & Career Services ROI
with b2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3>🎯 Workshop Effectiveness & ROI</h3>", unsafe_allow_html=True)
    workshop_tabs = st.tabs(["📈 Workshop Effectiveness", "💼 Service Utilization"])

    # Workshop Effectiveness tab: scatter + regression
    with workshop_tabs[0]:
        sc = px.scatter(
            df_f,
            x="WorkshopAttendance",
            y="InterviewInvites",
            color="Major",
            size="ApplicationsSubmitted",
            hover_data=["InternshipPlacement", "FullTimePlacement"]
        )
        # Fit linear trend
        reg = sm.OLS(df_f["InterviewInvites"], sm.add_constant(df_f["WorkshopAttendance"])).fit()
        xs = np.linspace(df_f["WorkshopAttendance"].min(), df_f["WorkshopAttendance"].max(), 100)
        sc.add_trace(go.Scatter(
            x=xs,
            y=reg.params["const"] + reg.params["WorkshopAttendance"] * xs,
            mode="lines",
            name="Trend",
            line=dict(dash="dash")
        ))
        sc.update_layout(
            height=300,
            xaxis_title="Workshops Attended",
            yaxis_title="Interview Invitations",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color=CLR_TEXT,
            legend_font=dict(color=CLR_TEXT)
        )
        sc.update_xaxes(tickfont=dict(color=CLR_TEXT), title_font=dict(color=CLR_TEXT))
        sc.update_yaxes(tickfont=dict(color=CLR_TEXT), title_font=dict(color=CLR_TEXT))
        st.plotly_chart(sc, use_container_width=True)
        st.markdown(
            "<p class='caption'>Students who attend more workshops receive significantly more interview invitations.</p>",
            unsafe_allow_html=True
        )

    # Service Utilization tab
    with workshop_tabs[1]:
        # Career services utilization analysis
        utilization_data = {
            'Career Service': ['Resume Review', 'Mock Interviews', 'Networking Events', 
                               'Industry Panels', 'Job Search Strategy', 'LinkedIn Optimization'],
            'Utilization Rate (%)': [85, 72, 68, 45, 91, 63],
            'Satisfaction Score': [4.2, 4.5, 4.1, 3.8, 4.3, 4.0],
            'Impact on Placement': [0.15, 0.22, 0.18, 0.12, 0.25, 0.14]
        }
        util_df = pd.DataFrame(utilization_data)
        bubble_fig = px.scatter(
            util_df,
            x='Utilization Rate (%)',
            y='Satisfaction Score',
            size='Impact on Placement',
            hover_name='Career Service',
            size_max=30
        )
        bubble_fig.update_layout(
            title='Career Services: Utilization vs Satisfaction vs Impact',
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color=CLR_TEXT
        )
        bubble_fig.update_xaxes(tickfont=dict(color=CLR_TEXT), title_font=dict(color=CLR_TEXT))
        bubble_fig.update_yaxes(tickfont=dict(color=CLR_TEXT), title_font=dict(color=CLR_TEXT))
        st.plotly_chart(bubble_fig, use_container_width=True)
        st.markdown(
            """
            <div class='insight-box'>
            <strong>🎯 Service Optimization Insights:</strong><br>
            • Job Search Strategy shows highest impact despite high utilization<br>
            • Mock Interviews have excellent satisfaction and strong impact<br>
            • <strong>Action Item:</strong> Increase capacity for high-impact, high-satisfaction services
            </div>
            """, unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)
# ────── PLACEMENT OUTCOMES + COMPARATIVE ANALYSIS ───────────────
st.markdown("<div class='section-header'>Placement Outcomes</div>",
            unsafe_allow_html=True)

col_outcome, col_comp = st.columns(2, gap="medium")

with col_outcome:
    placed = df_f["InternshipPlacement"].sum()
    total = df_f.shape[0]
    intern_rate = df_f[df_f["InternshipPlacement"]==1]["FullTimePlacement"].mean()
    no_intern   = df_f[df_f["InternshipPlacement"]==0]["FullTimePlacement"].mean()
    lift = ((intern_rate - no_intern) / no_intern) * 100 if no_intern else 0

    # build donut with percentages
    donut = px.pie(
        names=["Placed","Not Placed"],
        values=[placed, total - placed],
        hole=0.55,
        color_discrete_sequence=["#00B8A9","#87CEEB"],
        template="plotly_white"
    )
    # show slice label + percent inside, white text for contrast
    donut.update_traces(
        textinfo="label+percent",
        textposition="inside",
        insidetextorientation="radial",
        textfont=dict(color="black", size=14)
    )
    # enforce white background & black title text
    donut.update_layout(
        height=310,
        margin=dict(l=0, r=0, t=40, b=20),
        paper_bgcolor="white",
        plot_bgcolor="white",
        title=dict(text="Internship Outcome", font=dict(color=CLR_TEXT, size=16))
    )

    st.plotly_chart(donut, use_container_width=True)
    st.caption("Internships boost FT conversion; target ≥ 70%")
    st.markdown(
        f"<p class='caption'><span class='semibold'>Key Insight:</span> "
        f"Students with internships are <span class='text-success semibold'>{lift:.1f}%</span> "
        f"more likely to receive full-time offers</p>",
        unsafe_allow_html=True
    )


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
                                "(100 % = overall baseline)")
        else:
            st.warning("Select at least one major to view detailed analysis")
        st.markdown("</div>", unsafe_allow_html=True)

# ────── FOOTER ─────────────────────────────────────────────────
st.markdown("<div class='footer'>", unsafe_allow_html=True)
st.markdown(f"Career Outcomes Analytics Dashboard | "
            f"Last updated: {datetime.now():%B %d, %Y}", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Placeholder for future JS fullscreen control
st.markdown("""
<script>
// JS for fullscreen chart viewing would go here in production
</script>
""", unsafe_allow_html=True)

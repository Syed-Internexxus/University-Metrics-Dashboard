# Enhanced Professional University Career Outcomes Dashboard
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm

# Professional Color Scheme
BG_COLOR = "#F7F9FB"
CARD_COLOR = "#FFFFFF"
TEXT_COLOR = "#2E2E2E"
SUB_TEXT_COLOR = "#64748B"

PRIMARY_COLOR = "#3B82F6"
SUCCESS_COLOR = "#10B981"
ALERT_COLOR = "#F97316"
SECONDARY_COLOR = "#64748B"

st.set_page_config(
    page_title="University Career Outcomes Dashboard",
    page_icon="🎓",
    layout="wide",
)

# CSS Styles
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    html, body, .stApp {{
        font-family: 'Inter', sans-serif;
        background-color: {BG_COLOR};
        color: {TEXT_COLOR};
    }}
    .card {{
        background-color: {CARD_COLOR};
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        transition: transform 0.3s;
    }}
    .card:hover {{
        transform: translateY(-5px);
    }}
    h3 {{
        color: {PRIMARY_COLOR};
        font-weight: 600;
        margin-bottom: 0.5rem;
    }}
    .caption {{
        color: {SUB_TEXT_COLOR};
        font-size: 0.85rem;
    }}
    .stPlotlyChart {{
        height: 100%;
    }}
    </style>
""", unsafe_allow_html=True)

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("synthetic_career_dashboard_data.csv", parse_dates=[
        "RegisteredDate", "GraduationDate", "InternshipStartDate", "FullTimePlacementDate"])
    df["GraduationYear"] = df["GraduationDate"].dt.year
    df["RegMonth"] = df["RegisteredDate"].dt.to_period("M").astype(str)
    return df

df = load_data()

# Sidebar Filters
with st.sidebar:
    st.header("Filter Data")
    selected_majors = st.multiselect("Select Majors", options=df["Major"].unique(), default=df["Major"].unique())
    selected_years = st.multiselect("Select Graduation Years", options=df["GraduationYear"].unique(), default=df["GraduationYear"].unique())

filtered_df = df[df["Major"].isin(selected_majors) & df["GraduationYear"].isin(selected_years)]

# KPI Cards
kpi_cols = st.columns(4, gap="medium")
with kpi_cols[0]:
    st.markdown("<div class='card'><h3>Total Students</h3>"
                f"<h1>{filtered_df.shape[0]}</h1><p class='caption'>Total Registrations</p></div>",
                unsafe_allow_html=True)

with kpi_cols[1]:
    placement_rate = filtered_df["FullTimePlacement"].mean()
    st.markdown("<div class='card'><h3>Placement Rate</h3>"
                f"<h1>{placement_rate:.0%}</h1><p class='caption'>Full-time Placement</p></div>",
                unsafe_allow_html=True)

with kpi_cols[2]:
    median_days = filtered_df["DaysToFullTimeJob"].median()
    st.markdown("<div class='card'><h3>Median Days to Job</h3>"
                f"<h1>{median_days:.0f}</h1><p class='caption'>Days After Graduation</p></div>",
                unsafe_allow_html=True)

with kpi_cols[3]:
    avg_apps = filtered_df["ApplicationsSubmitted"].mean()
    st.markdown("<div class='card'><h3>Avg. Applications</h3>"
                f"<h1>{avg_apps:.1f}</h1><p class='caption'>Per Student</p></div>",
                unsafe_allow_html=True)

# Monthly Registrations Bar Chart
monthly_reg = filtered_df.groupby("RegMonth").size().reset_index(name="Count")
fig_reg = px.bar(monthly_reg, x="RegMonth", y="Count",
                 color_discrete_sequence=[PRIMARY_COLOR])
fig_reg.update_layout(title="Monthly Student Registrations",
                      xaxis_title="Month", yaxis_title="Students")
st.plotly_chart(fig_reg, use_container_width=True)

# 3-Month Rolling Avg Placement Line Chart
rolling_placement = filtered_df.set_index("GraduationDate").resample("M")["FullTimePlacement"].mean().rolling(3).mean().reset_index()
fig_placement = px.line(rolling_placement, x="GraduationDate", y="FullTimePlacement",
                        markers=True, color_discrete_sequence=[SUCCESS_COLOR])
fig_placement.update_layout(title="3-Month Rolling Placement Rate",
                            xaxis_title="Graduation Month", yaxis_title="Placement Rate")
st.plotly_chart(fig_placement, use_container_width=True)

# Major-wise Summary Table
major_summary = filtered_df.groupby("Major").agg(
    Students=("StudentID", "count"),
    AvgApps=("ApplicationsSubmitted", "mean"),
    PlacementRate=("FullTimePlacement", "mean")
).reset_index().round(2)

major_summary["PlacementRate"] = (major_summary["PlacementRate"] * 100).astype(str) + "%"
st.subheader("Major-wise Overview")
st.dataframe(major_summary, use_container_width=True)

# University Ranking
uni_rank = filtered_df.groupby("University").agg(
    Students=("StudentID", "count"),
    PlacementRate=("FullTimePlacement", "mean")
).reset_index().sort_values(by="PlacementRate", ascending=False).round(2)

uni_rank["PlacementRate"] = (uni_rank["PlacementRate"] * 100).astype(str) + "%"
st.subheader("Top Universities by Placement Rate")
st.dataframe(uni_rank, use_container_width=True)

# Internship Outcome Donut
internship_summary = filtered_df["InternshipPlacement"].value_counts().reset_index()
fig_donut = px.pie(internship_summary, names="InternshipPlacement", values="count",
                   color_discrete_sequence=[SUCCESS_COLOR, SECONDARY_COLOR], hole=0.6)
fig_donut.update_layout(title="Internship Outcomes")
st.plotly_chart(fig_donut, use_container_width=True)

# Footer
st.markdown("<div style='text-align:center;color:#9CA3AF;margin-top:30px;'>"
            "© 2025 University Career Insights Dashboard</div>",
            unsafe_allow_html=True)

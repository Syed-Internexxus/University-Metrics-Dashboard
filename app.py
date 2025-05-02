import pandas as pd, numpy as np, streamlit as st
import plotly.express as px, plotly.graph_objects as go
import statsmodels.api as sm
from datetime import datetime

# ───── Palette from screenshot ───────────────────────────────────
CLR_MINT   = "#16D5A8"
CLR_SKY_A  = "#C6E5F6"
CLR_SKY_B  = "#C5EBF0"
CLR_SKY_C  = "#D9F8F0"
CLR_SKY_D  = "#BCD9FB"
CLR_TEXT   = "#1F2B46"
CLR_CARD   = "#FFFFFF"
CLR_SHADOW = "rgba(26,39,77,.09)"

# ───── Page meta ────────────────────────────────────────────────
st.set_page_config(page_title="Career Outcomes Dashboard",
                   page_icon="📊",
                   layout="wide")

# ───── Global CSS (new background rules) ────────────────────────
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

    /* === Bright gradient background everywhere === */
    html, body, .stApp, .main, .block-container {{
        background:{CLR_SKY_C};
        background: radial-gradient(ellipse at 25% 15%,
                                    {CLR_SKY_C} 0%,
                                    {CLR_SKY_B} 35%,
                                    {CLR_SKY_D} 70%,
                                    {CLR_SKY_A} 100%);
        color:{CLR_TEXT};
        font-family:'Poppins',sans-serif;
    }}

    /* === Cards === */
    .card {{
        background:{CLR_CARD};
        padding:1.25rem 1.35rem;
        border-radius:14px;
        box-shadow:0 8px 18px {CLR_SHADOW};
        transition:transform .25s;
    }}
    .card:hover {{ transform:translateY(-4px); }}
    .card h3 {{ font-size:1rem; color:{CLR_MINT}; margin:0 0 .25rem 0; letter-spacing:.3px; }}
    .card h1 {{ font-size:2.25rem; line-height:1.1; margin:0; }}
    .caption {{ font-size:.78rem; color:#667693; margin-top:.25rem; }}

    /* === Sidebar === */
    section[data-testid="stSidebar"] > div:first-child {{
        background:{CLR_CARD};
        border-right:1px solid #E6EEF7;
    }}
    .stSidebar header, .stSidebar h1, .stSidebar h2, .stSidebar h3 {{
        color:{CLR_MINT};
    }}

    /* === Plotly container === */
    .stPlotlyChart{{ height:100%; }}

    /* === Scrollbar === */
    ::-webkit-scrollbar{{ width:8px; }}
    ::-webkit-scrollbar-thumb{{ background:{CLR_SKY_D}; border-radius:8px; }}
    </style>
    """,
    unsafe_allow_html=True
)

# ── Load dataset ────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_df():
    df = pd.read_csv(
        "synthetic_career_dashboard_data.csv",
        parse_dates=[
            "RegisteredDate","GraduationDate",
            "InternshipStartDate","FullTimePlacementDate",
        ],
    )
    df["GraduationYear"] = df["GraduationDate"].dt.year
    df["RegMonth"] = df["RegisteredDate"].dt.to_period("M").astype(str)
    return df

df   = load_df()
maj  = sorted(df["Major"].unique())
yrs  = sorted(df["GraduationYear"].unique())

# ── Sidebar filters ─────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    majors_f = st.multiselect("Major", maj, maj)
    years_f  = st.multiselect("Grad Year", yrs, yrs)

df_f = df[df["Major"].isin(majors_f) & df["GraduationYear"].isin(years_f)]

# ── Helper: sparkline ───────────────────────────────────────────
def spark(data, y, color=CLR_MINT):
    fig = px.line(data, y=y)
    fig.update_traces(showlegend=False, line=dict(color=color, width=2.5))
    fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=110,
                      xaxis_visible=False, yaxis_visible=False,
                      template="plotly_white")
    return fig


import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ------------------------------------------------------
# Fetch Liquidity Parameters
# ------------------------------------------------------
@st.cache_data(ttl=300)
def get_liquidity_parameters():
    """Fetch liquidity parameters from Reya Network API."""
    url = "https://api.reya.xyz/v2/liquidityParameters"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

data = get_liquidity_parameters()
df = pd.DataFrame(data)

# Fix numerical fields
df["depth"] = pd.to_numeric(df["depth"], errors="coerce")
df["velocityMultiplier"] = pd.to_numeric(df["velocityMultiplier"], errors="coerce")

# Create Liquidity Score
df["liquidityScore"] = df["depth"] * df["velocityMultiplier"]

# ------------------------------------------------------
# Derived KPIs
# ------------------------------------------------------
# Market Stability: Higher depth and lower velocity = more stable
df["stabilityScore"] = df["depth"] / df["velocityMultiplier"]

# Efficiency: Liquidity Score relative to Depth
df["efficiencyScore"] = df["liquidityScore"] / df["depth"]

# Risk Index: Low depth and high velocity = higher risk
df["riskIndex"] = df["velocityMultiplier"] / (df["depth"] + 1e-6)

# ------------------------------------------------------
# Streamlit Page Setup
# ------------------------------------------------------
st.set_page_config(
    page_title="Reya Network — Advanced Liquidity Dashboard",
    layout="wide"
)

st.title("💧 Reya Network — Advanced Liquidity Dashboard")

st.markdown("""
Welcome to the **advanced analytics dashboard** for Reya Network’s Liquidity Parameters.  
This interface provides deeper insights into liquidity depth, velocity characteristics, and derived liquidity-strength indicators.
""")

# ------------------------------------------------------
# Field Description Card (Green)
# ------------------------------------------------------
st.header("📘 Field Descriptions")
field_html = """
<div style="
    padding: 20px;
    border-radius: 10px;
    border: 1px solid #4caf50;
    background-color: #d9fdd3;
    line-height: 1.6;
">
    <p><b>symbol</b> — Market symbol associated with liquidity parameters.</p>
    <p><b>depth</b> — Represents the liquidity depth of the market.</p>
    <p><b>velocityMultiplier</b> — Indicates the speed at which liquidity adjusts in the market.</p>
    <p><b>liquidityScore</b> — Derived metric calculated as <b>depth × velocityMultiplier</b>.</p>
    <p><b>stabilityScore</b> — Higher = more stable market (depth high, velocity low).</p>
    <p><b>efficiencyScore</b> — Liquidity Score relative to depth (effectiveness of liquidity).</p>
    <p><b>riskIndex</b> — Higher = more risk due to shallow depth & fast liquidity changes.</p>
    <p><b>ANY_ADDITIONAL_PROPERTY</b> — Additional fields may appear depending on market conditions or upgrades.</p>
</div>
"""
st.markdown(field_html, unsafe_allow_html=True)

# ------------------------------------------------------
# Top-Level KPIs
# ------------------------------------------------------
st.header("📌 Key Performance Indicators (KPIs)")

st.markdown("""
<div style="
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #4caf50;
    background-color: #d9fdd3;
">
These KPIs give a high-level overview of Reya Network's markets, helping users identify top liquidity markets, average behavior, and risk indicators.
</div>
""", unsafe_allow_html=True)

total_markets = df["symbol"].nunique()
max_depth = df["depth"].max()
avg_depth = df["depth"].mean()
max_velocity = df["velocityMultiplier"].max()
avg_velocity = df["velocityMultiplier"].mean()
top_liquidity_score = df["liquidityScore"].max()
top_liquidity_markets = df[df["liquidityScore"] == top_liquidity_score]["symbol"].tolist()
avg_stability = df["stabilityScore"].mean()
avg_efficiency = df["efficiencyScore"].mean()
avg_risk = df["riskIndex"].mean()

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total Markets", total_markets)
k2.metric("Avg Depth", f"{avg_depth:.2f}")
k3.metric("Avg Velocity Multiplier", f"{avg_velocity:.2f}")
k4.metric("Top Liquidity Score", f"{top_liquidity_score:.2f}", 
          delta=f"Markets: {', '.join(top_liquidity_markets)}")
k5.metric("Avg Stability Score", f"{avg_stability:.2f}")
k6.metric("Avg Efficiency Score", f"{avg_efficiency:.2f}")

# ------------------------------------------------------
# Full Liquidity Table
# ------------------------------------------------------
st.header("📄 Full Liquidity Parameters Table")
st.dataframe(df, use_container_width=True)

# ------------------------------------------------------
# Top Markets Table
# ------------------------------------------------------
st.subheader("🏆 Top 10 Markets by Liquidity Score")
top_df = df.sort_values("liquidityScore", ascending=False).head(10)
st.table(top_df[["symbol", "depth", "velocityMultiplier", "liquidityScore", "stabilityScore", "efficiencyScore", "riskIndex"]])

# ------------------------------------------------------
# Visual Analytics
# ------------------------------------------------------
st.header("📊 Visual Analytics")

st.markdown("""
<div style="
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #4caf50;
    background-color: #d9fdd3;
">
These charts help visualize liquidity dynamics: how depth and velocity interact, the distribution of velocity multipliers, and overall liquidity efficiency.
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

# ---- Scatter Plot: Depth vs Velocity ----
with col1:
    st.subheader("📈 Depth vs Velocity Scatter Plot")
    fig_scatter = px.scatter(
        df,
        x="depth",
        y="velocityMultiplier",
        size="liquidityScore",
        color="liquidityScore",
        hover_name="symbol",
        title="Depth vs Velocity with Liquidity Score"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# ---- Donut Chart: Velocity Distribution ----
with col2:
    st.subheader("🟣 Velocity Multiplier Distribution")
    vel_counts = df["velocityMultiplier"].value_counts().reset_index()
    vel_counts.columns = ["velocityMultiplier", "count"]
    fig_donut = go.Figure(data=[go.Pie(
        labels=vel_counts["velocityMultiplier"],
        values=vel_counts["count"],
        hole=0.5
    )])
    fig_donut.update_layout(title_text="Velocity Multiplier Share")
    st.plotly_chart(fig_donut, use_container_width=True)

# ---- Bar Chart: Top Liquidity Score ----
st.subheader("📊 Top 10 Liquidity Markets")
fig_ls = px.bar(
    top_df,
    x="symbol",
    y="liquidityScore",
    color="liquidityScore",
    title="Top Liquidity Markets (by Liquidity Score)"
)
st.plotly_chart(fig_ls, use_container_width=True)

# ---- Correlation Heatmap ----
st.subheader("🔗 Correlation Matrix")
corr = df[["depth", "velocityMultiplier", "liquidityScore", "stabilityScore", "efficiencyScore", "riskIndex"]].corr()
fig_corr = px.imshow(
    corr,
    color_continuous_scale="Blues",
    text_auto=True,
    title="Correlation Heatmap"
)
st.plotly_chart(fig_corr, use_container_width=True)

# ---- Histogram: Depth Distribution ----
st.subheader("📊 Depth Distribution")
fig_hist = px.histogram(df, x="depth", nbins=20, title="Liquidity Depth Distribution Across Markets")
st.plotly_chart(fig_hist, use_container_width=True)

# ---- Bubble Chart: Stability vs Efficiency ----
st.subheader("💧 Stability vs Efficiency (Bubble Chart)")
fig_bubble = px.scatter(
    df,
    x="stabilityScore",
    y="efficiencyScore",
    size="liquidityScore",
    color="riskIndex",
    hover_name="symbol",
    color_continuous_scale="Viridis",
    title="Stability vs Efficiency with Liquidity and Risk"
)
st.plotly_chart(fig_bubble, use_container_width=True)

# ------------------------------------------------------
# Market Explorer
# ------------------------------------------------------
st.header("🔍 Market Details Explorer")
selected_market = st.selectbox("Select a market:", df["symbol"].unique())
selected_row = df[df["symbol"] == selected_market].iloc[0]
st.subheader(f"📌 Full Details for `{selected_market}`")
st.json(selected_row.to_dict())

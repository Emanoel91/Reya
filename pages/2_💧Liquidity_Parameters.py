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
# Streamlit Page Setup
# ------------------------------------------------------
st.set_page_config(
    page_title="Reya Network — Advanced Liquidity Dashboard",
    layout="wide"
)

st.title("💧 Reya Network — Advanced Liquidity Parameters Dashboard")

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
    <p><b>ANY_ADDITIONAL_PROPERTY</b> — Additional fields may appear depending on market conditions or upgrades.</p>
</div>
"""
st.markdown(field_html, unsafe_allow_html=True)


# ------------------------------------------------------
# KPIs
# ------------------------------------------------------
st.header("📌 Key Performance Indicators (KPIs)")

total_markets = df["symbol"].nunique()
max_depth = df["depth"].max()
avg_depth = df["depth"].mean()

max_velocity = df["velocityMultiplier"].max()
avg_velocity = df["velocityMultiplier"].mean()

top_liquidity_score = df["liquidityScore"].max()
top_liquidity_markets = df[df["liquidityScore"] == top_liquidity_score]["symbol"].tolist()

k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Markets", total_markets)
k2.metric("Avg Depth", f"{avg_depth:.3f}")
k3.metric("Avg Velocity Multiplier", f"{avg_velocity:.3f}")
k4.metric("Top Liquidity Score", f"{top_liquidity_score:.3f}", 
          delta=f"Markets: {', '.join(top_liquidity_markets)}")


# ------------------------------------------------------
# Full Table
# ------------------------------------------------------
st.header("📄 Full Liquidity Parameters Table")
st.dataframe(df, use_container_width=True)


# ------------------------------------------------------
# Top Liquidity Markets Table
# ------------------------------------------------------
st.subheader("🏆 Top Markets by Liquidity Score")

top_df = df.sort_values("liquidityScore", ascending=False).head(10)
st.table(top_df[["symbol", "depth", "velocityMultiplier", "liquidityScore"]])


# ------------------------------------------------------
# Visual Analytics
# ------------------------------------------------------
st.header("📊 Visual Analytics")

col1, col2 = st.columns(2)

# ---- Scatter Plot ----
with col1:
    st.subheader("📈 Depth vs Velocity (Scatter Plot)")
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

# ---- Donut Chart for Velocity ----
with col2:
    st.subheader("🟣 Velocity Multiplier Distribution (Donut Chart)")
    vel_counts = df["velocityMultiplier"].value_counts().reset_index()
    vel_counts.columns = ["velocityMultiplier", "count"]

    fig_donut = go.Figure(
        data=[go.Pie(
            labels=vel_counts["velocityMultiplier"],
            values=vel_counts["count"],
            hole=0.5
        )]
    )
    fig_donut.update_layout(title_text="Velocity Multiplier Share")
    st.plotly_chart(fig_donut, use_container_width=True)


# ------------------------------------------------------
# Liquidity Score Bar Chart
# ------------------------------------------------------
st.subheader("📈 Top 10 Liquidity Score (Bar Chart)")
fig_ls = px.bar(
    top_df,
    x="symbol",
    y="liquidityScore",
    color="liquidityScore",
    title="Top Liquidity Markets (by Liquidity Score)"
)
st.plotly_chart(fig_ls, use_container_width=True)


# ------------------------------------------------------
# Correlation Matrix
# ------------------------------------------------------
st.subheader("🔗 Correlation Matrix (Depth vs Velocity vs Liquidity Score)")

corr = df[["depth", "velocityMultiplier", "liquidityScore"]].corr()

fig_corr = px.imshow(
    corr,
    color_continuous_scale="Blues",
    text_auto=True,
    title="Correlation Heatmap"
)
st.plotly_chart(fig_corr, use_container_width=True)


# ------------------------------------------------------
# Market Explorer
# ------------------------------------------------------
st.header("🔍 Market Details Explorer")

selected_market = st.selectbox("Select a market:", df["symbol"].unique())
selected_row = df[df["symbol"] == selected_market].iloc[0]

st.subheader(f"📌 Full Details for `{selected_market}`")
st.json(selected_row.to_dict())

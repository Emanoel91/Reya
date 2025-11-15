import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import math

# ----------------------------
# Fetch Liquidity Parameters
# ----------------------------
@st.cache_data(ttl=300)
def get_liquidity_parameters():
    url = "https://api.reya.xyz/v2/liquidityParameters"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

data = get_liquidity_parameters()
df = pd.DataFrame(data)

# Ensure numeric
df["depth"] = pd.to_numeric(df["depth"], errors="coerce").fillna(0.0)
df["velocityMultiplier"] = pd.to_numeric(df["velocityMultiplier"], errors="coerce").fillna(0.0)

# Derived base metric
df["liquidityScore"] = df["depth"] * df["velocityMultiplier"]

# ----------------------------
# Derived KPIs used below
# ----------------------------
# Stability: more depth and lower velocity => higher stability
# avoid division by zero
df["stabilityScore"] = df["depth"] / (df["velocityMultiplier"] + 1e-12)

# Efficiency: liquidityScore relative to depth (if depth==0 -> 0)
df["efficiencyScore"] = df.apply(lambda r: (r["liquidityScore"] / r["depth"]) if r["depth"] > 0 else 0.0, axis=1)

# Risk index: higher when velocity high and depth low
df["riskIndex"] = df.apply(lambda r: (r["velocityMultiplier"] / (r["depth"] + 1e-12)), axis=1)

# Undervalued metric: markets with relatively high depth but low liquidityScore
# We use depth / (liquidityScore + eps) so higher => more "undervalued" (depth high vs liquidityScore)
df["undervaluedMetric"] = df.apply(lambda r: (r["depth"] / (r["liquidityScore"] + 1e-12)) if (r["liquidityScore"] > 0) else np.inf, axis=1)

# Market Attractiveness: per your formula
# We choose variance = variance of (depth * velocityMultiplier) across markets (i.e., variance of liquidityScore)
global_variance = df["liquidityScore"].var(ddof=0)
eps = 1e-12
if global_variance is None or np.isclose(global_variance, 0.0):
    # fallback to 1 to avoid division by zero
    global_variance = 1.0
df["attractivenessIndex"] = df.apply(
    lambda r: np.log(max(r["depth"] * r["velocityMultiplier"], eps)) / global_variance, axis=1
)

# ----------------------------
# Streamlit Page Setup
# ----------------------------
st.set_page_config(page_title="Reya — Advanced Liquidity Dashboard (Final)", layout="wide")
st.title("💧 Reya Network — Advanced Liquidity Dashboard (Final)")

st.markdown("""
This dashboard presents liquidity parameters and derived KPIs for Reya markets.
All explanatory text boxes required are in English and shown in pale green cards before each KPI/chart.
""")

# ---------- Helper: green card ----------
def green_card_html(text: str):
    return f"""
    <div style="
        padding:12px;
        border-radius:10px;
        border:1px solid #4caf50;
        background-color:#eafbe9;
        color: #042b16;
        margin-bottom:8px;
        line-height:1.4;
    ">{text}</div>
    """

# ----------------------------
# Row 1: Liquidity Score KPIs
# ----------------------------
st.header("📌 Liquidity Score Overview (Row 1)")

# KPI values
max_liq_val = df["liquidityScore"].max()
max_liq_markets = df[df["liquidityScore"] == max_liq_val]["symbol"].tolist()
min_liq_val = df["liquidityScore"].min()
min_liq_markets = df[df["liquidityScore"] == min_liq_val]["symbol"].tolist()
avg_liq = df["liquidityScore"].mean()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Highest Liquidity Score", value=f"{max_liq_val:.6g}")
    st.caption("Market(s): " + ", ".join(max_liq_markets))
    st.markdown(green_card_html("<b>What this means:</b> The market shown above has the highest Liquidity Score and is therefore the most 'stable' market for large orders."), unsafe_allow_html=True)

with col2:
    st.metric(label="Lowest Liquidity Score", value=f"{min_liq_val:.6g}")
    st.caption("Market(s): " + ", ".join(min_liq_markets))
    st.markdown(green_card_html("<b>What this means:</b> The market shown above has the lowest Liquidity Score and is therefore the least stable (most prone to price impact)."), unsafe_allow_html=True)

with col3:
    st.metric(label="Average Liquidity Score (Reya)", value=f"{avg_liq:.6g}")
    st.markdown(green_card_html("<b>What this means:</b> The average Liquidity Score across all Reya markets — a quick baseline for comparison."), unsafe_allow_html=True)

# English explanation row after KPIs (as requested)
st.markdown(green_card_html(
    "<b>Liquidity Score indicates which markets are the 'most stable' and 'least costly' for large orders, and vice versa. "
    "Based on the Liquidity Score, users can quickly see which assets will provide the best trading experience.</b>"
), unsafe_allow_html=True)

st.markdown("---")

# ----------------------------
# Row 2: Velocity Multiplier KPIs
# ----------------------------
st.header("📌 Velocity Multiplier Overview (Row 2)")

max_vel = df["velocityMultiplier"].max()
max_vel_markets = df[df["velocityMultiplier"] == max_vel]["symbol"].tolist()
min_vel = df["velocityMultiplier"].min()
min_vel_markets = df[df["velocityMultiplier"] == min_vel]["symbol"].tolist()
avg_vel = df["velocityMultiplier"].mean()

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Highest Velocity Multiplier", f"{max_vel:.6g}")
    st.caption("Market(s): " + ", ".join(max_vel_markets))
with c2:
    st.metric("Lowest Velocity Multiplier", f"{min_vel:.6g}")
    st.caption("Market(s): " + ", ".join(min_vel_markets))
with c3:
    st.metric("Average Velocity Multiplier (Reya)", f"{avg_vel:.6g}")

# English explanation after these KPIs
vel_text = (
    "<b>Traders, momentum traders and scalpers highly value the Velocity Multiplier because it indicates how fast market liquidity "
    "adjusts to new conditions (trade volume or volatility).<br><br>"
    "🔸 A larger number = faster market adaptation. <br>"
    "🔸 A smaller number = slower liquidity changes.</b>"
)
st.markdown(green_card_html(vel_text), unsafe_allow_html=True)

st.markdown("_________________________________________________________________________")

# ----------------------------
# Row 3: Full Liquidity Parameters Table (index starting at 1)
# ----------------------------
st.header("📄 Full Liquidity Parameters Table (Row 3)")

df_table = df.copy()
# set index starting from 1 for display only
df_table_display = df_table.reset_index(drop=True)
df_table_display.index = range(1, len(df_table_display) + 1)
st.dataframe(df_table_display, use_container_width=True)

st.markdown("___________________________________________________________________________")

# ----------------------------
# Row 4: Market Details Explorer
# ----------------------------
st.header("🔍 Market Details Explorer (Row 4)")
st.markdown(green_card_html("<b>Select a market to inspect full details. The JSON and radar chart (later) are populated from this selection.</b>"), unsafe_allow_html=True)
selected_market = st.selectbox("Select a market:", df["symbol"].unique())
selected_row = df[df["symbol"] == selected_market].iloc[0]
st.subheader(f"📌 Full Details for `{selected_market}`")
st.json(selected_row.to_dict())

st.markdown("____________________________________________________________________________")

# ----------------------------
# Row 5: Top 10 Most Liquid Markets
# ----------------------------
st.header("🏆 Top 10 Most Liquid Markets (Row 5)")
top10_liquid = df.sort_values("liquidityScore", ascending=False).head(10).copy()
top10_liquid_display = top10_liquid.reset_index(drop=True)
top10_liquid_display.index = range(1, len(top10_liquid_display) + 1)
st.table(top10_liquid_display[["symbol", "depth", "velocityMultiplier", "liquidityScore"]])

st.markdown("______________________________________________________________________________________")

# ----------------------------
# Row 6: Top 10 Most Volatile Liquidity Markets (by velocityMultiplier)
# ----------------------------
st.header("⚡ Top 10 Most Volatile Liquidity Markets (Row 6)")
top10_volatile = df.sort_values("velocityMultiplier", ascending=False).head(10).copy()
top10_volatile_display = top10_volatile.reset_index(drop=True)
top10_volatile_display.index = range(1, len(top10_volatile_display) + 1)
st.table(top10_volatile_display[["symbol", "depth", "velocityMultiplier", "liquidityScore"]])

st.markdown("________________________________________________________________________________")

# ----------------------------
# Row 7: Scatter (depth vs liquidityScore) + Undervalued horizontal bar (top 10)
# ----------------------------
st.header("📊 Depth vs Liquidity Score & Undervalued Markets (Row 7)")

st.markdown(green_card_html("<b>Left: Scatter plot showing depth (x) vs liquidityScore (y). Right: Undervalued markets — those with high depth but relatively low liquidityScore. Top 10 shown.</b>"), unsafe_allow_html=True)

r7c1, r7c2 = st.columns([2, 1])

with r7c1:
    fig_scat_dl = px.scatter(
        df,
        x="depth",
        y="liquidityScore",
        hover_name="symbol",
        size="depth",  # emphasize bigger depth
        color="riskIndex",
        color_continuous_scale="Turbo",
        title="Depth (x) vs Liquidity Score (y)"
    )
    fig_scat_dl.update_layout(xaxis_title="Depth", yaxis_title="Liquidity Score")
    st.plotly_chart(fig_scat_dl, use_container_width=True)

with r7c2:
    # Undervalued: sort by undervaluedMetric descending, show top10
    undervalued_top10 = df.sort_values("undervaluedMetric", ascending=False).head(10).copy()
    undervalued_top10["label"] = undervalued_top10["symbol"]
    # horizontal bar
    fig_underval = px.bar(
        undervalued_top10[::-1],
        x="undervaluedMetric",
        y="label",
        orientation="h",
        title="Top 10 Undervalued Liquidity Markets (depth high & liquidityScore low)",
        labels={"undervaluedMetric": "Depth / LiquidityScore", "label": "Market"}
    )
    st.plotly_chart(fig_underval, use_container_width=True)

st.markdown("__________________________________________________________________________________")

# ----------------------------
# Row 8: Scatter (depth vs velocity) + High-Risk top10 horizontal bar
# ----------------------------
st.header("📊 Depth vs Velocity & High-Risk Markets (Row 8)")

st.markdown(green_card_html("<b>Left: Scatter plot showing depth (x) vs velocityMultiplier (y). Right: Top 10 High-Risk markets (depth low & velocity high) by riskIndex.</b>"), unsafe_allow_html=True)

r8c1, r8c2 = st.columns([2, 1])

with r8c1:
    fig_scat_dv = px.scatter(
        df,
        x="depth",
        y="velocityMultiplier",
        hover_name="symbol",
        size="liquidityScore",
        color="riskIndex",
        color_continuous_scale="Inferno",
        title="Depth (x) vs Velocity Multiplier (y)"
    )
    fig_scat_dv.update_layout(xaxis_title="Depth", yaxis_title="Velocity Multiplier")
    st.plotly_chart(fig_scat_dv, use_container_width=True)

with r8c2:
    highrisk_top10 = df.sort_values("riskIndex", ascending=False).head(10).copy()
    highrisk_top10["label"] = highrisk_top10["symbol"]
    fig_highrisk = px.bar(
        highrisk_top10[::-1],
        x="riskIndex",
        y="label",
        orientation="h",
        title="Top 10 High-Risk Markets (depth low & velocity high)",
        labels={"riskIndex": "Risk Index", "label": "Market"}
    )
    st.plotly_chart(fig_highrisk, use_container_width=True)

st.markdown("_______________________________________________________________________________")

# ----------------------------
# Row 9: Market Attractiveness Index table (index starting at 1)
# ----------------------------
st.header("⭐ Market Attractiveness Index (Row 9)")

st.markdown(green_card_html("<b>Attractiveness = log(depth × velocityMultiplier) / variance (variance of liquidityScore across markets). Higher means more attractive per this heuristic.</b>"), unsafe_allow_html=True)

attract_df = df.sort_values("attractivenessIndex", ascending=False).copy()
attract_display = attract_df[["symbol", "depth", "velocityMultiplier", "liquidityScore", "attractivenessIndex"]].reset_index(drop=True)
attract_display.index = range(1, len(attract_display) + 1)
st.table(attract_display)

st.markdown("________________________________________________________________________________")

# ----------------------------
# Row 10: Radar Chart per selected market
# ----------------------------
st.header("📡 Radar Chart (Row 10) — Select Market")

st.markdown(green_card_html("<b>Select a market to visualize its profile across depth, velocityMultiplier and liquidityScore.</b>"), unsafe_allow_html=True)

radar_market = st.selectbox("Choose market for Radar Chart:", df["symbol"].unique(), key="radar_select")
row = df[df["symbol"] == radar_market].iloc[0]

# prepare radar
categories = ["depth", "velocityMultiplier", "liquidityScore"]
values = [row["depth"], row["velocityMultiplier"], row["liquidityScore"]]
# To make radar closed
values += [values[0]]
categories += [categories[0]]

fig_radar = go.Figure(
    data=[
        go.Scatterpolar(r=values, theta=categories, fill='toself', name=radar_market)
    ],
    layout=go.Layout(
        title=go.layout.Title(text=f"Radar Profile — {radar_market}"),
        polar=dict(
            radialaxis=dict(visible=True)
        )
    )
)
st.plotly_chart(fig_radar, use_container_width=True)

# ----------------------------
# Footer / Notes
# ----------------------------
st.markdown("---")
st.markdown("""
**Notes & Methodology:**  
- `stabilityScore = depth / velocityMultiplier` (higher => more stable).  
- `efficiencyScore = liquidityScore / depth` (approx equals velocityMultiplier where depth>0).  
- `riskIndex = velocityMultiplier / depth` (higher => more risky).  
- `undervaluedMetric = depth / liquidityScore` (higher => more depth relative to liquidityScore).  
- `attractivenessIndex` uses the global variance of liquidityScore to normalize; if variance is zero a fallback is applied.  
- Table indices shown in this dashboard start from 1 as requested.
""")

import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- Page Config ------------------------------------------------------------------------------------------------------
st.set_page_config(
    page_title="Reya",
    page_icon="https://img.cryptorank.io/coins/reya_labs_voltz1733895726081.png",
    layout="wide"
)
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
df["stabilityScore"] = df["depth"] / (df["velocityMultiplier"] + 1e-12)
df["efficiencyScore"] = df.apply(lambda r: (r["liquidityScore"] / r["depth"]) if r["depth"] > 0 else 0.0, axis=1)
df["riskIndex"] = df.apply(lambda r: (r["velocityMultiplier"] / (r["depth"] + 1e-12)), axis=1)
df["undervaluedMetric"] = df.apply(lambda r: (r["depth"] / (r["liquidityScore"] + 1e-12)) if (r["liquidityScore"] > 0) else np.inf, axis=1)

# ----------------------------
# Streamlit Page Setup
# ----------------------------
st.set_page_config(page_title="Reya — Advanced Liquidity Dashboard (Final)", layout="wide")
st.title("💧 Reya — Liquidity Parameters")

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

# Highest
max_liq_val = df["liquidityScore"].max()
max_liq_markets = df[df["liquidityScore"] == max_liq_val]["symbol"].tolist()

# Lowest (ignore zeros)
min_liq_val = df[df["liquidityScore"] > 0]["liquidityScore"].min()
min_liq_markets = df[df["liquidityScore"] == min_liq_val]["symbol"].tolist()

# Average
avg_liq = df["liquidityScore"].mean()
total_markets = len(df)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Highest Liquidity Score", f"{max_liq_val:.6g}")
    st.caption("Market(s): " + ", ".join(max_liq_markets))

with col2:
    st.metric("Lowest Liquidity Score (non-zero)", f"{min_liq_val:.6g}")
    st.caption("Market(s): " + ", ".join(min_liq_markets))

with col3:
    st.metric("Average Liquidity Score (Reya)", f"{avg_liq:.6g}")
    st.caption(f"{total_markets} markets")

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

# Lowest (ignore zeros)
min_vel = df[df["velocityMultiplier"] > 0]["velocityMultiplier"].min()
min_vel_markets = df[df["velocityMultiplier"] == min_vel]["symbol"].tolist()

avg_vel = df["velocityMultiplier"].mean()

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Highest Velocity Multiplier", f"{max_vel:.6g}")
    st.caption("Market(s): " + ", ".join(max_vel_markets))

with c2:
    st.metric("Lowest Velocity Multiplier (non-zero)", f"{min_vel:.6g}")
    st.caption("Market(s): " + ", ".join(min_vel_markets))

with c3:
    st.metric("Average Velocity Multiplier (Reya)", f"{avg_vel:.6g}")

vel_text = (
    "<b>Traders, momentum traders and scalpers highly value the Velocity Multiplier because it indicates how fast market liquidity "
    "adjusts to new conditions (trade volume or volatility).<br><br>"
    "🔸 A larger number = faster market adaptation. <br>"
    "🔸 A smaller number = slower liquidity changes.</b>"
)
st.markdown(green_card_html(vel_text), unsafe_allow_html=True)

st.markdown("_________________________________________________________________________")

# ----------------------------
# Row 3: Full Liquidity Parameters Table (index from 1)
# ----------------------------
st.header("📄 Full Liquidity Parameters Table (Row 3)")

df_table = df.copy()
df_table_display = df_table.reset_index(drop=True)
df_table_display.index = range(1, len(df_table_display) + 1)
st.dataframe(df_table_display, use_container_width=True)

st.markdown("___________________________________________________________________________")

# ----------------------------
# Row 4: Market Details Explorer
# ----------------------------
st.header("🔍 Market Details Explorer (Row 4)")

st.markdown(green_card_html("<b>Select a market to inspect full details.</b>"), unsafe_allow_html=True)
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
# Row 6: Top 10 Most Volatile Markets
# ----------------------------
st.header("⚡ Top 10 Most Volatile Liquidity Markets (Row 6)")

top10_volatile = df.sort_values("velocityMultiplier", ascending=False).head(10).copy()
top10_volatile_display = top10_volatile.reset_index(drop=True)
top10_volatile_display.index = range(1, len(top10_volatile_display) + 1)
st.table(top10_volatile_display[["symbol", "depth", "velocityMultiplier", "liquidityScore"]])

st.markdown("________________________________________________________________________________")

# ----------------------------
# Row 7: Scatter + Undervalued Markets with label values
# ----------------------------
st.header("📊 Depth vs Liquidity Score & Undervalued Markets (Row 7)")

st.markdown(green_card_html("<b>Left: Depth vs Liquidity Score scatter. Right: Undervalued markets (high depth + low liquidityScore).</b>"), unsafe_allow_html=True)

r7c1, r7c2 = st.columns([2, 1])

with r7c1:
    fig_scat_dl = px.scatter(
        df,
        x="depth",
        y="liquidityScore",
        hover_name="symbol",
        size="depth",
        color="riskIndex",
        color_continuous_scale="Turbo",
        title="Depth (x) vs Liquidity Score (y)"
    )
    st.plotly_chart(fig_scat_dl, use_container_width=True)

with r7c2:
    undervalued_top10 = df.sort_values("undervaluedMetric", ascending=False).head(10).copy()
    undervalued_top10["label"] = undervalued_top10["symbol"]

    fig_underval = px.bar(
        undervalued_top10[::-1],
        x="undervaluedMetric",
        y="label",
        orientation="h",
        title="Top 10 Undervalued Liquidity Markets",
        labels={"undervaluedMetric": "Depth / LiquidityScore", "label": "Market"}
    )

    # add labels to bars
    fig_underval.update_traces(
        text=undervalued_top10[::-1]["undervaluedMetric"].round(3),
        textposition="outside"
    )

    st.plotly_chart(fig_underval, use_container_width=True)

st.markdown("__________________________________________________________________________________")

# ----------------------------
# Row 8: Scatter + High-Risk Table
# ----------------------------
st.header("📊 Depth vs Velocity & High-Risk Markets (Row 8)")

st.markdown(green_card_html("<b>Left: Depth vs Velocity scatter. Right: Top 10 High-Risk markets (depth low + velocity high).</b>"), unsafe_allow_html=True)

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
    st.plotly_chart(fig_scat_dv, use_container_width=True)

with r8c2:
    highrisk_top10 = df.sort_values("riskIndex", ascending=False).head(10).copy()
    highrisk_top10_display = highrisk_top10.reset_index(drop=True)
    highrisk_top10_display.index = range(1, len(highrisk_top10_display) + 1)
    st.table(highrisk_top10_display[["symbol", "riskIndex"]])

st.markdown("_______________________________________________________________________________")

# ----------------------------
# Row 9 removed (Market Attractiveness Index)
# ----------------------------

# ----------------------------
# Row 10: Radar Chart per market
# ----------------------------
st.header("📡 Radar Chart (Row 10) — Select Market")

st.markdown(green_card_html("<b>Select a market to visualize its profile across depth, velocityMultiplier and liquidityScore.</b>"), unsafe_allow_html=True)

radar_market = st.selectbox("Choose market for Radar Chart:", df["symbol"].unique(), key="radar_select")
row = df[df["symbol"] == radar_market].iloc[0]

categories = ["depth", "velocityMultiplier", "liquidityScore"]
values = [row["depth"], row["velocityMultiplier"], row["liquidityScore"]]

categories += [categories[0]]
values += [values[0]]

fig_radar = go.Figure(
    data=[
        go.Scatterpolar(r=values, theta=categories, fill='toself', name=radar_market)
    ],
    layout=go.Layout(
        title=go.layout.Title(text=f"Radar Profile — {radar_market}"),
        polar=dict(radialaxis=dict(visible=True))
    )
)

st.plotly_chart(fig_radar, use_container_width=True)


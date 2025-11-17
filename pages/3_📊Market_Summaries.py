# market_summary_full.py
"""
Reya Network — Market Summary Dashboard (Updated)
Changes requested:
 - Add index starting from 1 ONLY in the Full Raw Table
 - Convert updatedAt & pricesUpdatedAt UNIX timestamps to readable datetime
 - Remove row indices in all other tables
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

API_URL = "https://api.reya.xyz/v2/markets/summary"

@st.cache_data(ttl=1)
def fetch_market_summary():
    resp = requests.get(API_URL, timeout=10)
    resp.raise_for_status()
    return resp.json()

# ----------------------------- Fetch Data -----------------------------------
try:
    raw = fetch_market_summary()
except Exception as e:
    st.set_page_config(page_title="Reya Market Summary (Error)", layout="wide")
    st.title("❌ Error Loading Market Summary")
    st.error(f"Could not fetch data: {e}")
    st.stop()

df = pd.DataFrame(raw)

# ----------------------------- Numeric Fields --------------------------------
numeric_cols = [
    "longOiQty", "shortOiQty", "oiQty", "fundingRate",
    "longFundingValue", "shortFundingValue", "fundingRateVelocity",
    "volume24h", "pxChange24h", "throttledOraclePrice", "throttledPoolPrice"
]

def ensure_numeric(df_in, cols):
    df_out = df_in.copy()
    for c in cols:
        df_out[c] = pd.to_numeric(df_out.get(c), errors="coerce")
    return df_out

df = ensure_numeric(df, numeric_cols)

# ----------------------------- Timestamp Conversion --------------------------
def convert_unix_to_str(val):
    """Convert UNIX ms → readable format."""
    try:
        return datetime.fromtimestamp(int(val) / 1000).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return ""

df["updatedAt_str"] = df["updatedAt"].apply(convert_unix_to_str) if "updatedAt" in df else ""
df["pricesUpdatedAt_str"] = df["pricesUpdatedAt"].apply(convert_unix_to_str) if "pricesUpdatedAt" in df else ""

# ----------------------------- Derived Metrics --------------------------------
df["oiImbalance"] = df["longOiQty"] - df["shortOiQty"]
df["priceSpread"] = df["throttledPoolPrice"] - df["throttledOraclePrice"]
df["fundingPressure"] = df["fundingRate"] * df["oiImbalance"]
df["normalizedFunding"] = df["fundingRate"] / df["throttledOraclePrice"].replace(0, np.nan)
df["absPriceSpread"] = df["priceSpread"].abs()

# ----------------------------- Page Config -----------------------------------
st.set_page_config(page_title="Reya Market Summary Dashboard", layout="wide")
st.title("📊 Reya Network — Market Summary Dashboard")

# ----------------------------- Field Description ------------------------------
st.header("📘 Field Descriptions")
desc_html = """
<div style="padding:16px;border-radius:10px;border:1px solid #4caf50;background-color:#eafbea;line-height:1.6">
  <b>symbol</b> — Market symbol.<br>
  <b>updatedAt</b> — Timestamp (converted to local datetime).<br>
  <b>longOiQty</b>, <b>shortOiQty</b>, <b>oiQty</b> — Open interest metrics.<br>
  <b>fundingRate</b> — Funding rate; + means longs pay shorts.<br>
  <b>fundingRateVelocity</b> — Change rate of funding.<br>
  <b>volume24h</b> — Past 24h volume.<br>
  <b>pxChange24h</b> — Price change 24h.<br>
  <b>Pool vs Oracle price</b> — AMM vs external oracle.<br>
  <b>Derived Metrics</b><br>
  • oiImbalance = long - short<br>
  • priceSpread = pool - oracle<br>
  • fundingPressure = funding × imbalance<br>
  • normalizedFunding = funding / price<br>
</div>
"""
st.markdown(desc_html, unsafe_allow_html=True)

# ----------------------------- KPIs ------------------------------------------
st.header("📌 Key Performance Indicators")

total_markets = df["symbol"].nunique()
total_volume = df["volume24h"].sum(min_count=1)
total_oi = df["oiQty"].sum(min_count=1)
total_long = df["longOiQty"].sum(min_count=1)
total_short = df["shortOiQty"].sum(min_count=1)
avg_funding = df["fundingRate"].mean()

# Leaders
max_vol = df["volume24h"].max()
max_vol_markets = df[df["volume24h"] == max_vol]["symbol"].tolist()

max_oi = df["oiQty"].max()
max_oi_markets = df[df["oiQty"] == max_oi]["symbol"].tolist()

top_pos_funding = df.sort_values("fundingRate", ascending=False).head(3)
top_neg_funding = df.sort_values("fundingRate").head(3)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Markets", f"{total_markets}")
k2.metric("Network 24h Volume", f"{total_volume:,.2f}")
k3.metric("Total OI", f"{total_oi:,.4f}")
k4.metric("Avg Funding Rate", f"{avg_funding:.6f}")

k5, k6, k7, k8 = st.columns(4)
k5.metric("Top Volume Market(s)", ", ".join(max_vol_markets), f"{max_vol:,.2f}")
k6.metric("Top OI Market(s)", ", ".join(max_oi_markets), f"{max_oi:,.4f}")
k7.metric("Long OI", f"{total_long:,.4f}")
k8.metric("Short OI", f"{total_short:,.4f}")

# ----------------------------- FULL RAW TABLE --------------------------------
st.markdown("---")
st.subheader("📄 Full Market Summary Table (raw & derived)")

df_display = df.copy()

# Remove internal numeric timestamps
for col in ["updatedAt", "pricesUpdatedAt"]:
    if col in df_display.columns:
        del df_display[col]

# Add index column starting at 1
df_display.insert(0, "#", range(1, len(df_display) + 1))

st.dataframe(df_display, use_container_width=True)

# ----------------------------- Leaderboards ----------------------------------
st.markdown("---")
st.header("🏆 Leaderboards & Market Rankings")

colA, colB = st.columns(2)

with colA:
    st.markdown("### Top Positive Funding Rates")
    st.table(
        top_pos_funding[["symbol", "fundingRate"]]
        .assign(fundingRate=lambda x: x["fundingRate"].map(lambda v: f"{v:.6f}"))
        .reset_index(drop=True)   # remove index
    )

with colB:
    st.markdown("### Top Negative Funding Rates")
    st.table(
        top_neg_funding[["symbol", "fundingRate"]]
        .assign(fundingRate=lambda x: x["fundingRate"].map(lambda v: f"{v:.6f}"))
        .reset_index(drop=True)
    )

st.markdown("### Price Divergence (Pool vs Oracle)")
price_div = df[["symbol", "throttledOraclePrice", "throttledPoolPrice", "priceSpread", "absPriceSpread"]]
price_div = price_div.sort_values("absPriceSpread", ascending=False)
st.table(
    price_div.assign(
        throttledOraclePrice=lambda d: d["throttledOraclePrice"].map(lambda v: f"{v:.6f}"),
        throttledPoolPrice=lambda d: d["throttledPoolPrice"].map(lambda v: f"{v:.6f}"),
        priceSpread=lambda d: d["priceSpread"].map(lambda v: f"{v:.6f}"),
        absPriceSpread=lambda d: d["absPriceSpread"].map(lambda v: f"{v:.6f}")
    ).reset_index(drop=True)
)

st.markdown("### Top 24h Volume Markets")
vol_tbl = df[["symbol", "volume24h", "pxChange24h", "oiQty"]].sort_values("volume24h", ascending=False)
st.table(
    vol_tbl.assign(
        volume24h=lambda d: d["volume24h"].map(lambda v: f"{v:,.2f}"),
        pxChange24h=lambda d: d["pxChange24h"].map(lambda v: f"{v:.4f}"),
        oiQty=lambda d: d["oiQty"].map(lambda v: f"{v:.4f}")
    ).reset_index(drop=True)
)

# ----------------------------- CHARTS ----------------------------------------
st.markdown("---")
st.header("📊 Visual Analytics")

col1, col2 = st.columns((2, 1))

with col1:
    st.subheader("📈 Long vs Short Open Interest (Stacked)")
    oi_plot = df[["symbol", "longOiQty", "shortOiQty", "oiQty"]].fillna(0).sort_values("oiQty", ascending=False).head(40)
    fig_stack = go.Figure()
    fig_stack.add_trace(go.Bar(x=oi_plot["symbol"], y=oi_plot["longOiQty"], name="Long OI"))
    fig_stack.add_trace(go.Bar(x=oi_plot["symbol"], y=oi_plot["shortOiQty"], name="Short OI"))
    fig_stack.update_layout(barmode="stack", xaxis_tickangle=-45, height=450)
    st.plotly_chart(fig_stack, use_container_width=True)

    st.subheader("📉 Funding Rate Distribution")
    fig_hist = px.histogram(df, x="fundingRate", nbins=40)
    fig_hist.update_layout(height=350)
    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    st.subheader("🟣 Total Long vs Short OI (Donut)")
    fig_donut = go.Figure(go.Pie(
        labels=["Long OI", "Short OI"],
        values=[total_long, total_short],
        hole=0.55
    ))
    fig_donut.update_layout(height=350)
    st.plotly_chart(fig_donut, use_container_width=True)

    st.subheader("⚡ Funding Rate Velocity (Top 30)")
    fv = df[["symbol", "fundingRateVelocity"]].sort_values("fundingRateVelocity", ascending=False).head(30)
    fig_fv = px.bar(fv, x="symbol", y="fundingRateVelocity")
    fig_fv.update_layout(xaxis_tickangle=45, height=300)
    st.plotly_chart(fig_fv, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.subheader("🔎 Volume vs 24h Price Change")
    scatter_df = df.dropna(subset=["volume24h", "pxChange24h"])
    fig_sc = px.scatter(
        scatter_df,
        x="pxChange24h",
        y="volume24h",
        size="oiQty",
        color="fundingRate",
        hover_name="symbol",
        log_y=True
    )
    st.plotly_chart(fig_sc, use_container_width=True)

with col4:
    st.subheader("🔺 Absolute Price Spread")
    pdv = df[["symbol", "absPriceSpread"]].sort_values("absPriceSpread", ascending=False).head(40)
    fig_div = px.bar(pdv, x="symbol", y="absPriceSpread")
    fig_div.update_layout(xaxis_tickangle=45, height=450)
    st.plotly_chart(fig_div, use_container_width=True)

# ----------------------------- Market Explorer --------------------------------
st.markdown("---")
st.header("🔍 Market Details Explorer")

symbols = df["symbol"].unique().tolist()
chosen = st.selectbox("Select market:", ["(none)"] + symbols)

if chosen != "(none)":
    row = df[df["symbol"] == chosen].iloc[0]

    st.subheader(f"Summary: {chosen}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Oracle Price", f"{row['throttledOraclePrice']:,.6f}")
    c2.metric("Pool Price", f"{row['throttledPoolPrice']:,.6f}")
    c3.metric("Spread", f"{row['priceSpread']:.6f}")

    st.metric("OI (long / short / total)",
              f"{row['longOiQty']} / {row['shortOiQty']} / {row['oiQty']}")

    st.metric("Funding Rate", f"{row['fundingRate']:.6f}")

    clean_json = row.dropna().to_dict()
    st.json(clean_json)

# ----------------------------- END --------------------------------------------
st.markdown("---")
st.markdown("Dashboard generated using Reya Network real-time summary API.")

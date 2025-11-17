# market_summary_full.py
"""
Reya Network — Market Summary Dashboard (complete)
Consumes: https://api.reya.xyz/v2/markets/summary

Features:
 - Field descriptions card
 - KPIs (total markets, total volume, total OI, top markets, funding leaders, price divergence)
 - Full data table
 - Derived metrics (OI imbalance, priceSpread, fundingPressure, normalizedFunding)
 - Charts (OI bar, stacked long/short OI, donut long vs short, funding histogram,
         funding velocity bar, volume vs price-change scatter, price divergence bar)
 - Useful tables: Funding Leaderboard, Price Divergence, Top Volume Markets
 - Market Details Explorer (per-market JSON + small summary)
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
# --- Page Config ------------------------------------------------------------------------------------------------------
st.set_page_config(
    page_title="Reya — Liquidity Parameters",
    page_icon="https://img.cryptorank.io/coins/reya_labs_voltz1733895726081.png",
    layout="wide")
# --- Sidebar Footer Slightly Left-Aligned ---------------------------------------------------------------------
st.sidebar.markdown(
    """
    <style>
    .sidebar-footer {
        position: fixed;
        bottom: 20px;
        width: 250px;
        font-size: 13px;
        color: gray;
        margin-left: 5px; 
        text-align: left;  
    }
    .sidebar-footer img {
        width: 16px;
        height: 16px;
        vertical-align: middle;
        border-radius: 50%;
        margin-right: 5px;
    }
    .sidebar-footer a {
        color: gray;
        text-decoration: none;
    }
    </style>

    <div class="sidebar-footer">
        <div>
            <a href="https://x.com/Reya_xyz" target="_blank">
                <img src="https://img.cryptorank.io/coins/reya_labs_voltz1733895726081.png" alt="Reya Logo">
                Powered by Reya
            </a>
        </div>
        <div style="margin-top: 5px;">
            <a href="https://x.com/0xeman_raz" target="_blank">
                <img src="https://pbs.twimg.com/profile_images/1841479747332608000/bindDGZQ_400x400.jpg" alt="Eman Raz">
                Built by Eman Raz
            </a>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
# -------------------------
# Configuration
# -------------------------
API_URL = "https://api.reya.xyz/v2/markets/summary"

# cache for ~1 second to avoid hammering the API; values are recalculated frequently server-side
@st.cache_data(ttl=1)
def fetch_market_summary():
    """Fetch summary statistics for all markets from Reya API."""
    resp = requests.get(API_URL, timeout=10)
    resp.raise_for_status()
    return resp.json()

# -------------------------
# Fetch & normalize data
# -------------------------
try:
    raw = fetch_market_summary()
except Exception as e:
    st.set_page_config(page_title="Reya Market Summary (error)", layout="wide")
    st.title("📊 Reya — Market Summary")
    st.error(f"Failed to fetch data from {API_URL}: {e}")
    st.stop()

# Convert to DataFrame
df = pd.DataFrame(raw)

# Safe numeric conversion helper
def ensure_numeric(df_in, cols):
    df_out = df_in.copy()
    for c in cols:
        if c in df_out.columns:
            df_out[c] = pd.to_numeric(df_out[c], errors="coerce")
        else:
            df_out[c] = np.nan
    return df_out

numeric_cols = [
    "longOiQty", "shortOiQty", "oiQty", "fundingRate",
    "longFundingValue", "shortFundingValue", "fundingRateVelocity",
    "volume24h", "pxChange24h", "throttledOraclePrice", "throttledPoolPrice"
]
df = ensure_numeric(df, numeric_cols)

# timestamps (if present)
for ts_col in ["updatedAt", "pricesUpdatedAt"]:
    if ts_col in df.columns:
        # Some timestamps may be in ms since epoch
        def _ts_to_dt(x):
            try:
                return datetime.fromtimestamp(int(x) / 1000.0)
            except Exception:
                return pd.NaT
        df[ts_col + "_dt"] = df[ts_col].apply(_ts_to_dt)

# Derived metrics
df["oiImbalance"] = df["longOiQty"] - df["shortOiQty"]
df["priceSpread"] = df["throttledPoolPrice"] - df["throttledOraclePrice"]
df["fundingPressure"] = df["fundingRate"] * df["oiImbalance"]
# normalized funding (fundingRate relative to price) — avoid div by zero
df["normalizedFunding"] = df["fundingRate"] / df["throttledOraclePrice"].replace(0, np.nan)
df["absPriceSpread"] = df["priceSpread"].abs()

# -------------------------
# Page Setup
# -------------------------
st.set_page_config(page_title="Reya Market Summary — Full Dashboard", layout="wide")
st.title("📊 Reya — Market Summary")
st.markdown(
    "Real-time market summaries (recalculated frequently). "
    "This dashboard surfaces Open Interest, Funding, Volume, Price signals, and derived indicators."
)

# -------------------------
# Field Descriptions Card
# -------------------------
st.header("📘 Field Descriptions")
desc_html = """
<div style="padding:16px;border-radius:10px;border:1px solid #4caf50;background-color:#eafbea;line-height:1.6">
  <b>symbol</b> — Market symbol (e.g., BTCRUSDPERP).<br>
  <b>updatedAt</b> — Timestamp for last update (ms epoch).<br>
  <b>longOiQty</b> / <b>shortOiQty</b> / <b>oiQty</b> — Open interest (long, short, total).<br>
  <b>fundingRate</b> — Current funding rate (periodic). Positive: longs pay shorts.<br>
  <b>longFundingValue</b> / <b>shortFundingValue</b> — Funding payment values.<br>
  <b>fundingRateVelocity</b> — Rate of change of fundingRate.<br>
  <b>volume24h</b> — 24-hour traded volume.<br>
  <b>pxChange24h</b> — Price change over 24h (raw value from API).<br>
  <b>throttledOraclePrice</b> / <b>throttledPoolPrice</b> — Price sources (throttled updates).<br>
  <b>Derived:</b> oiImbalance = longOiQty - shortOiQty; priceSpread = pool - oracle;<br>
  fundingPressure = fundingRate × oiImbalance; normalizedFunding = fundingRate / price.
</div>
"""
st.markdown(desc_html, unsafe_allow_html=True)

# -------------------------
# KPI Section
# -------------------------
st.header("📌 Key Performance Indicators")

# safe aggregates
total_markets = int(df["symbol"].nunique()) if "symbol" in df.columns else 0
total_volume_24h = df["volume24h"].sum(min_count=1)
total_oi = df["oiQty"].sum(min_count=1)
total_long_oi = df["longOiQty"].sum(min_count=1)
total_short_oi = df["shortOiQty"].sum(min_count=1)
avg_funding = df["fundingRate"].mean()
avg_price_spread = df["absPriceSpread"].mean()

# highest volume market(s)
if "volume24h" in df.columns and not df["volume24h"].isna().all():
    max_vol = df["volume24h"].max()
    max_vol_markets = df.loc[df["volume24h"] == max_vol, "symbol"].dropna().unique().tolist()
else:
    max_vol = np.nan
    max_vol_markets = []

# highest OI market(s)
if "oiQty" in df.columns and not df["oiQty"].isna().all():
    max_oi = df["oiQty"].max()
    max_oi_markets = df.loc[df["oiQty"] == max_oi, "symbol"].dropna().unique().tolist()
else:
    max_oi = np.nan
    max_oi_markets = []

# funding leaders
top_positive_funding = df.sort_values("fundingRate", ascending=False).head(3)[["symbol", "fundingRate"]]
top_negative_funding = df.sort_values("fundingRate", ascending=True).head(3)[["symbol", "fundingRate"]]

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Markets", f"{total_markets:,}")
k2.metric("Network 24h Volume", f"{total_volume_24h:,.2f}", help="Sum of volume24h across markets")
k3.metric("Network Total OI", f"{total_oi:,.4f}", help="Sum of oiQty across markets")
k4.metric("Avg Funding Rate", f"{avg_funding:.6f}" if not np.isnan(avg_funding) else "N/A")

# second row of KPIs
k5, k6, k7, k8 = st.columns(4)
k5.metric("Top Volume Market(s)", ", ".join(max_vol_markets) if max_vol_markets else "N/A", f"{max_vol:,.2f}" if not np.isnan(max_vol) else "")
k6.metric("Top OI Market(s)", ", ".join(max_oi_markets) if max_oi_markets else "N/A", f"{max_oi:,.4f}" if not np.isnan(max_oi) else "")
k7.metric("Total Long OI", f"{total_long_oi:,.4f}")
k8.metric("Total Short OI", f"{total_short_oi:,.4f}")

# -------------------------
# Full Data Table (collapsible)
# -------------------------
st.markdown("---")
with st.expander("📄 Full Market Summary Table (raw & derived)"):
    st.dataframe(df.fillna("").sort_values("symbol"), use_container_width=True)

# -------------------------
# Top tables: Funding leaderboard, Price divergence, Top volume
# -------------------------
st.markdown("---")
st.subheader("🏆 Leaderboards & Price Divergence")

# Funding leaderboard (top positive and most negative)
colA, colB = st.columns(2)

with colA:
    st.markdown("**Top Positive Funding Rates (longs pay shorts)**")
    if not top_positive_funding.empty:
        st.table(top_positive_funding.assign(fundingRate=lambda x: x["fundingRate"].map(lambda v: f"{v:.6f}")))
    else:
        st.write("No funding data available.")

with colB:
    st.markdown("**Top Negative Funding Rates (shorts pay longs)**")
    if not top_negative_funding.empty:
        st.table(top_negative_funding.assign(fundingRate=lambda x: x["fundingRate"].map(lambda v: f"{v:.6f}")))
    else:
        st.write("No funding data available.")

# Price divergence table
st.markdown("**Price Divergence (Pool vs Oracle)**")
if "absPriceSpread" in df.columns:
    price_div_table = df[["symbol", "throttledOraclePrice", "throttledPoolPrice", "priceSpread", "absPriceSpread"]].copy()
    price_div_table = price_div_table.sort_values("absPriceSpread", ascending=False).head(20)
    st.table(price_div_table.assign(
        throttledOraclePrice=lambda d: d["throttledOraclePrice"].map(lambda v: f"{v:.6f}" if pd.notna(v) else "N/A"),
        throttledPoolPrice=lambda d: d["throttledPoolPrice"].map(lambda v: f"{v:.6f}" if pd.notna(v) else "N/A"),
        priceSpread=lambda d: d["priceSpread"].map(lambda v: f"{v:.6f}" if pd.notna(v) else "N/A"),
        absPriceSpread=lambda d: d["absPriceSpread"].map(lambda v: f"{v:.6f}" if pd.notna(v) else "N/A")
    ))
else:
    st.write("Price spread data not available.")

# Top volume markets table
st.markdown("**Top Markets by 24h Volume**")
if "volume24h" in df.columns:
    top_vol = df[["symbol", "volume24h", "pxChange24h", "oiQty"]].sort_values("volume24h", ascending=False).head(20)
    st.table(top_vol.assign(
        volume24h=lambda d: d["volume24h"].map(lambda v: f"{v:,.2f}" if pd.notna(v) else "N/A"),
        pxChange24h=lambda d: d["pxChange24h"].map(lambda v: f"{v:.4f}" if pd.notna(v) else "N/A"),
        oiQty=lambda d: d["oiQty"].map(lambda v: f"{v:.4f}" if pd.notna(v) else "N/A"),
    ))
else:
    st.write("Volume data not available.")

# -------------------------
# Charts / Visual Analytics
# -------------------------------------------------------------------------------
# Column layout for multiple charts
# ====== Row 1 ======
row1_col1, row1_col2 = st.columns(2)

# ---------- Row 1 - Left ----------
with row1_col1:
    st.markdown("<h3 style='font-size:20px;'>📈 Open Interest by Market (Total & Breakdown)</h3>", unsafe_allow_html=True)

    oi_plot = df[["symbol", "longOiQty", "shortOiQty", "oiQty"]].copy().fillna(0)
    oi_plot = oi_plot.sort_values("oiQty", ascending=False).head(40)

    if not oi_plot.empty:
        fig_oi_stack = go.Figure()
        fig_oi_stack.add_trace(go.Bar(x=oi_plot["symbol"], y=oi_plot["longOiQty"], name="Long OI"))
        fig_oi_stack.add_trace(go.Bar(x=oi_plot["symbol"], y=oi_plot["shortOiQty"], name="Short OI"))
        fig_oi_stack.update_layout(
            barmode="stack",
            xaxis_tickangle=-45,
            height=450,
            title="Long vs Short Open Interest (stacked)"
        )
        st.plotly_chart(fig_oi_stack, use_container_width=True)
    else:
        st.write("No open interest data to plot.")

# ---------- Row 1 - Right ----------
with row1_col2:
    st.markdown("<h3 style='font-size:20px;'>💰 Funding Rate Distribution</h3>", unsafe_allow_html=True)

    if "fundingRate" in df.columns and not df["fundingRate"].isna().all():
        fig_fund_hist = px.histogram(df, x="fundingRate", nbins=40,
                                     title="Funding Rate Distribution")
        fig_fund_hist.update_layout(height=450)
        st.plotly_chart(fig_fund_hist, use_container_width=True)
    else:
        st.write("Funding rate data not available.")


# ====== Row 2 ======
row2_col1, row2_col2 = st.columns(2)

# ---------- Row 2 - Left ----------
with row2_col1:
    
    st.markdown("<h3 style='font-size:25px;'>⚖️ Long vs Short OI (Network)</h3>", unsafe_allow_html=True)

    total_long = total_long_oi if not np.isnan(total_long_oi) else 0
    total_short = total_short_oi if not np.isnan(total_short_oi) else 0

    fig_donut = go.Figure(data=[
        go.Pie(labels=["Long OI", "Short OI"], values=[total_long, total_short], hole=0.5)
    ])
    fig_donut.update_layout(title="Network Long vs Short OI", height=400)
    st.plotly_chart(fig_donut, use_container_width=True)

# ---------- Row 2 - Right ----------
with row2_col2:
    st.markdown("<h3 style='font-size:25px;'>⚡ Funding Rate Velocity (per Market)</h3>", unsafe_allow_html=True)

    if "fundingRateVelocity" in df.columns and not df["fundingRateVelocity"].isna().all():
        fv = df[["symbol", "fundingRateVelocity"]].sort_values(
            "fundingRateVelocity", ascending=False
        ).head(30)

        fig_fv = px.bar(fv, x="symbol", y="fundingRateVelocity",
                        title="Funding Rate Velocity (top 30)")
        fig_fv.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig_fv, use_container_width=True)
    else:
        st.write("Funding rate velocity not available.")

# -------------------------------------------------------------------------------------------------------------------
# Lower row: scatter and price divergence bar
col3, col4 = st.columns(2)

with col3:
    st.markdown("<h3 style='font-size:20px;'>🔎 Volume vs 24h Price Change (bubble: OI size)</h3>", unsafe_allow_html=True)
    if "volume24h" in df.columns and "pxChange24h" in df.columns:
        scatter_df = df.dropna(subset=["volume24h", "pxChange24h"])
        if not scatter_df.empty:
            fig_scatter = px.scatter(
                scatter_df,
                x="pxChange24h",
                y="volume24h",
                size="oiQty",
                color="fundingRate",
                hover_name="symbol",
                title="Volume vs Price Change (bubble size = oiQty)",
                log_y=True
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.write("Not enough data for scatter plot.")
    else:
        st.write("Volume or pxChange data not available.")

with col4:
    st.markdown("<h3 style='font-size:20px;'>🔺 Price Divergence by Market (abs(pool - oracle))</h3>", unsafe_allow_html=True)
    if "absPriceSpread" in df.columns and not df["absPriceSpread"].isna().all():
        pdv = df[["symbol", "absPriceSpread"]].sort_values("absPriceSpread", ascending=False).head(40)
        fig_div = px.bar(pdv, x="symbol", y="absPriceSpread", title="Absolute Price Spread (top 40)")
        fig_div.update_layout(xaxis_tickangle=-45, height=450)
        st.plotly_chart(fig_div, use_container_width=True)
    else:
        st.write("Price spread data not available.")

# -------------------------
# Market Explorer (detailed view)
# -------------------------
st.header("🔍 Market Details Explorer")

symbols = df["symbol"].dropna().unique().tolist()
chosen = st.selectbox("Select a market to inspect:", ["(none)"] + symbols)

if chosen and chosen != "(none)":
    row = df[df["symbol"] == chosen].iloc[0]
    # show nice mini-summary
    st.subheader(f"Summary — {chosen}")
    cols = st.columns(3)
    cols[0].metric("Oracle Price", f"{row.get('throttledOraclePrice', np.nan):,.6f}" if pd.notna(row.get('throttledOraclePrice', None)) else "N/A")
    cols[1].metric("Pool Price", f"{row.get('throttledPoolPrice', np.nan):,.6f}" if pd.notna(row.get('throttledPoolPrice', None)) else "N/A")
    cols[2].metric("Price Spread", f"{row.get('priceSpread', np.nan):,.6f}" if pd.notna(row.get('priceSpread', None)) else "N/A")
    st.metric("OI (long / short / total)", f"{row.get('longOiQty', 'N/A')} / {row.get('shortOiQty', 'N/A')} / {row.get('oiQty', 'N/A')}")
    st.metric("Funding Rate", f"{row.get('fundingRate', 'N/A')}")
    st.markdown("**Full JSON for selected market**")
    st.json(row.dropna().to_dict())

# -------------------------
# Finishing notes
# -------------------------
st.markdown("---")
st.markdown(
    "Notes: Data is provided by Reya Network's `markets/summary` endpoint. "
    "Fields and availability can vary by market. This dashboard computes derived metrics "
    "for analysis: OI imbalance, price spread, funding pressure, and normalized funding."
)

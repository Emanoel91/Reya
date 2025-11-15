import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ------------------------------------------------------
# Fetch Market Definitions
# ------------------------------------------------------
@st.cache_data(ttl=300)
def get_market_definitions():
    """Fetch market definitions from Reya Network API."""
    url = "https://api.reya.xyz/v2/marketDefinitions"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


data = get_market_definitions()
df = pd.DataFrame(data)


# ------------------------------------------------------
# Streamlit Page Setup
# ------------------------------------------------------
st.set_page_config(
    page_title="Reya Network Market Definitions Dashboard",
    layout="wide"
)

st.title("📊 Reya Network")

st.markdown("""
This dashboard visualizes and explains the **Market Definitions API** from the Reya Network.  
Explore field definitions, raw market data, visual analytics, and detailed information for each market.
""")


# ------------------------------------------------------
# Field Descriptions (Green Card Style)
# ------------------------------------------------------
st.header("📘 Field Descriptions")

field_block_html = """
<div style="
    padding: 20px;
    border-radius: 10px;
    border: 1px solid #4caf50;
    background-color: #d9fdd3;
    line-height: 1.6;
">
    <p><b>symbol</b> — Market symbol (e.g., BTCRUSDPERP for Bitcoin perpetual futures).</p>
    <p><b>marketId</b> — Unique numerical identifier assigned to each market.</p>
    <p><b>minOrderQty</b> — Minimum allowed order quantity.</p>
    <p><b>qtyStepSize</b> — Quantity increment; orders must follow this step size.</p>
    <p><b>tickSize</b> — Minimum price tick (smallest allowed price movement).</p>
    <p><b>initialMarginParameter</b> — Required initial margin parameter when opening a position.</p>
    <p><b>liquidationMarginParameter</b> — Margin parameter used to compute liquidation thresholds.</p>
    <p><b>maxLeverage</b> — Maximum leverage allowed for this market.</p>
    <p><b>oiCap</b> — Maximum allowed Open Interest for this market.</p>
</div>
"""

st.markdown(field_block_html, unsafe_allow_html=True)


# ------------------------------------------------------
# Display Raw Data Table
# ------------------------------------------------------
st.header("📄 Full Market Definitions Table")
st.dataframe(df, use_container_width=True)


# ------------------------------------------------------
# Market Details Explorer
# ------------------------------------------------------
st.header("🔍 Market Details Explorer")

markets = df["symbol"].unique()
selected = st.selectbox("Select a market:", markets)

selected_row = df[df["symbol"] == selected].iloc[0]

st.subheader(f"📌 Full Details for `{selected}`")
st.json(selected_row.to_dict())


# ------------------------------------------------------
# Visualization Section
# ------------------------------------------------------
st.header("📊 Visual Analytics")

# Ensure maxLeverage is numeric
df["maxLeverage"] = pd.to_numeric(df["maxLeverage"], errors="coerce")

# Drop rows with NaN maxLeverage to avoid plotting issues
df_plot = df.dropna(subset=["maxLeverage"])

# Prepare aggregated data for bar & donut charts
leverage_counts = df_plot["maxLeverage"].value_counts().reset_index()
leverage_counts.columns = ["maxLeverage", "count"]
leverage_counts = leverage_counts.sort_values("maxLeverage")


# ------------------------------------------------------
# Row with Column Bar Chart + Donut Chart
# ------------------------------------------------------
col_bar, col_donut = st.columns(2)

# -------- Column Bar Chart (Max Leverage Distribution) --------
with col_bar:
# --    st.subheader("📈 Max Leverage Distribution (Column Chart)")
    bar_fig = px.bar(
        leverage_counts,
        x="maxLeverage",
        y="count",
        labels={"maxLeverage": "Max Leverage", "count": "Count"},
        title="Max Leverage Frequency (Bar Chart)",
    )
    bar_fig.update_layout(xaxis_type="category")
    st.plotly_chart(bar_fig, use_container_width=True)

# -------- Donut Chart (Max Leverage) --------
with col_donut:
# --    st.subheader("🟣 Max Leverage Distribution (Donut Chart)")
    donut_fig = go.Figure(
        data=[
            go.Pie(
                labels=leverage_counts["maxLeverage"],
                values=leverage_counts["count"],
                hole=0.5
            )
        ]
    )
    donut_fig.update_layout(title_text="Max Leverage Share by Value")
    st.plotly_chart(donut_fig, use_container_width=True)

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

st.title("📊 Reya Network — Market Definitions Dashboard")

st.markdown("""
This dashboard visualizes and explains the **Market Definitions API** from the Reya Network.  
Explore field definitions, raw market data, charts, and market-level details.
""")


# ------------------------------------------------------
# Field Descriptions (Card Style)
# ------------------------------------------------------
st.header("📘 Field Descriptions")

field_descriptions = {
    "symbol": "Market symbol (e.g., BTCRUSDPERP for Bitcoin perpetual futures).",
    "marketId": "Unique numerical identifier assigned to each market.",
    "minOrderQty": "Minimum allowed order quantity.",
    "qtyStepSize": "Quantity increment; orders must follow this step size.",
    "tickSize": "Minimum price tick (smallest allowed price movement).",
    "initialMarginParameter": "Required initial margin parameter when opening a position.",
    "liquidationMarginParameter": "Margin parameter used to compute liquidation thresholds.",
    "maxLeverage": "Maximum leverage allowed for this market.",
    "oiCap": "Maximum allowed Open Interest for this market."
}

with st.container():
    st.markdown("""
    <div style="padding: 20px; border-radius: 10px; border: 1px solid #ccc; background-color: #f9f9f9;">
        <h4 style="margin-top: 0;">Field Definitions Overview</h4>
    """, unsafe_allow_html=True)

    for field, desc in field_descriptions.items():
        st.markdown(f"**`{field}`** — {desc}")

    st.markdown("</div>", unsafe_allow_html=True)


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

df["maxLeverage"] = pd.to_numeric(df["maxLeverage"], errors="coerce")


# ----------------------------------
# Max Leverage Bar Chart (Plotly)
# ----------------------------------
st.subheader("📈 Max Leverage Distribution (Bar Chart)")

bar_fig = px.histogram(
    df,
    x="maxLeverage",
    nbins=20,
    title="Max Leverage Histogram",
)

st.plotly_chart(bar_fig, use_container_width=True)


# ----------------------------------
# Donut Chart (Based on Max Leverage)
# ----------------------------------
st.subheader("🟣 Max Leverage Donut Chart")

# Count frequencies
leverage_counts = df["maxLeverage"].value_counts().reset_index()
leverage_counts.columns = ["maxLeverage", "count"]

donut_fig = go.Figure(
    data=[
        go.Pie(
            labels=leverage_counts["maxLeverage"],
            values=leverage_counts["count"],
            hole=0.5
        )
    ]
)

donut_fig.update_layout(title_text="Max Leverage Distribution (Donut Chart)")
st.plotly_chart(donut_fig, use_container_width=True)

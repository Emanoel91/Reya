import streamlit as st
import requests
import pandas as pd
import altair as alt

# ------------------------------------------------------
# Fetch Market Definitions from Reya Network API
# ------------------------------------------------------
@st.cache_data(ttl=300)
def get_market_definitions():
    """
    Fetch market definitions from Reya Network API.
    Cached for 300 seconds to avoid excessive requests.
    """
    url = "https://api.reya.xyz/v2/marketDefinitions"
    response = requests.get(url)
    return response.json()

data = get_market_definitions()

# Convert JSON to DataFrame
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
This dashboard visualizes and explains the **Market Definitions API** data from the **Reya Network**.

You will find:
- A complete explanation of all API fields  
- Raw market definition data  
- Visual analytics and distribution charts  
- A detailed market inspector  
- Statistical summaries  
""")

# ------------------------------------------------------
# Field Explanations (English)
# ------------------------------------------------------
st.header("📘 Field Descriptions")

field_descriptions = {
    "symbol": "The market symbol (e.g., BTCRUSDPERP for Bitcoin perpetual futures).",
    "marketId": "A unique numerical identifier assigned to each market.",
    "minOrderQty": "Minimum order quantity allowed for this market.",
    "qtyStepSize": "Order quantity increment; orders must be multiples of this value.",
    "tickSize": "Minimum allowable price change (price tick).",
    "initialMarginParameter": "Parameter defining how much initial margin is required to open a position.",
    "liquidationMarginParameter": "Parameter used to calculate liquidation margin level.",
    "maxLeverage": "Maximum leverage allowed for this market.",
    "oiCap": "Maximum allowed Open Interest for the market.",
}

for field, desc in field_descriptions.items():
    st.markdown(f"### 🔹 `{field}`")
    st.markdown(f"{desc}")
    st.markdown("---")


# ------------------------------------------------------
# Display Raw Data Table
# ------------------------------------------------------
st.header("📄 Full Market Definitions Table")
st.dataframe(df, use_container_width=True)


# ------------------------------------------------------
# Visualization Section
# ------------------------------------------------------
st.header("📊 Visualization & Analytics")

col1, col2 = st.columns(2)

# ------- Tick Size Chart -------
with col1:
    st.subheader("📈 Tick Size Distribution")
    try:
        df["tickSize"] = pd.to_numeric(df["tickSize"], errors="coerce")
        chart_tick = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                x=alt.X("tickSize:Q", title="Tick Size"),
                y=alt.Y("count()", title="Count"),
            )
        )
        st.altair_chart(chart_tick, use_container_width=True)
    except:
        st.warning("Tick Size values are not numeric or are missing.")

# ------- Max Leverage Chart -------
with col2:
    st.subheader("📈 Max Leverage Distribution")
    try:
        df["maxLeverage"] = pd.to_numeric(df["maxLeverage"], errors="coerce")
        chart_leverage = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                x=alt.X("maxLeverage:Q", title="Max Leverage"),
                y=alt.Y("count()", title="Count"),
            )
        )
        st.altair_chart(chart_leverage, use_container_width=True)
    except:
        st.warning("Max Leverage values are not numeric or are missing.")


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
# Statistical Summary
# ------------------------------------------------------
st.header("📊 Summary Statistics")

numeric_cols = [
    "minOrderQty", "qtyStepSize", "tickSize",
    "initialMarginParameter", "liquidationMarginParameter",
    "maxLeverage", "oiCap"
]

df_numeric = df.copy()

# Convert numeric fields
for col in numeric_cols:
    df_numeric[col] = pd.to_numeric(df_numeric[col], errors="coerce")

st.dataframe(df_numeric.describe(), use_container_width=True)

st.markdown("---")
st.markdown("Dashboard generated with ❤️ for Reya Network developers.")

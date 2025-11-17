import streamlit as st

# --- Page Config: Tab Title & Icon ---
st.set_page_config(
    page_title="Reya",
    page_icon="https://img.cryptorank.io/coins/reya_labs_voltz1733895726081.png",
    layout="wide"
)
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
# --- Title with Logo ---
st.markdown(
    """
    <div style="display: flex; align-items: center; gap: 15px;">
        <img src="https://img.cryptorank.io/coins/reya_labs_voltz1733895726081.png" alt="reya" style="width:60px; height:60px;">
        <h1 style="margin: 0;">Reya Dashboard</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Builder Info ------------------------------------------------------------------------

st.markdown(
    """
    <div style="margin-top: 20px; margin-bottom: 20px; font-size: 16px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <img src="https://pbs.twimg.com/profile_images/1841479747332608000/bindDGZQ_400x400.jpg" alt="Eman Raz" style="width:25px; height:25px; border-radius: 50%;">
            <span>Built by: <a href="https://x.com/0xeman_raz" target="_blank">Eman Raz</a></span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Info Box --------------------------------------------------------------------------------------------------------------
st.markdown(
    """
    <div style="background-color: #4bff99; padding: 10px; border-radius: 1px; border: 1px solid #000000;">
        <b>Reya</b> is a breakthrough high-performance onchain exchange that delivers <b>institutional grade execution</b>, whilst delivering superior 
        <b>speed</b>, <b>security</b> and <b>reliability</b> guarantees to users. Reya achieves this as a novel <b>trading-specific based Zk rollup</b> on Ethereum. 
        This design gives users superior:
        <br><br>
        🔸 <b>Speed</b>: &lt;1ms trade execution<br>
        🔸 <b>Security</b>: verifiable order execution and settlement, via zk-proofs, with executed trades settling on Ethereum<br>
        🔸 <b>Reliability</b>: no single point of failure, with the rollup design having multiple rotating L2 nodes (unlike generation-1 rollups)<br><br>
        The based-design also makes Reya <b>synchronously composable</b> with all of <b>Ethereum L1 DeFi</b>, unlocking novel use cases for traders and builders. 
        No sidecar. No Alt-L1. Instead, a <b>DEX enshrined into the Ethereum L1</b>.
    </div>
    """,
    unsafe_allow_html=True
)

# --- Reference and Rebuild Info -------------------------------------------------------------------------------------------
st.markdown(
    """
    <div style="margin-top: 20px; margin-bottom: 20px; font-size: 16px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <img src="https://img.cryptorank.io/coins/reya_labs_voltz1733895726081.png" alt="REYA" style="width:25px; height:25px; border-radius: 50%;">
            <span>Data Powered by: <a href="https://docs.reya.xyz/developers" target="_blank">Reya API</a></span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Links with Logos ---
st.markdown(
    """
    <div style="font-size: 16px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <img src="https://img.cryptorank.io/coins/reya_labs_voltz1733895726081.png" alt="reya" style="width:20px; height:20px;">
            <a href="https://reya.xyz/" target="_blank">Reya Website</a>
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
            <img src="https://img.cryptorank.io/coins/reya_labs_voltz1733895726081.png" alt="Reya X" style="width:20px; height:20px;">
            <a href="https://x.com/Reya_xyz" target="_blank">Reya X Account</a>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

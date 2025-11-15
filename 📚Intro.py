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
st.markdown("""
This dashboard visualizes and explains the **Market Definitions API** data from the **Reya Network**.

You will find:
- A complete explanation of all API fields  
- Raw market definition data  
- Visual analytics and distribution charts  
- A detailed market inspector  
- Statistical summaries  
""")
# --- Reference and Rebuild Info ---
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

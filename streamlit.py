import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import pandas_datareader.data as web
import plotly.express as px
from datetime import datetime, timedelta
import time
import pytz

# Configure the page
st.set_page_config(
    page_title="QuantEdge: Alpha Signal Research Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ✅ Enhanced CSS for metric boxes and layout
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #f0f2f6;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 15px;
        word-wrap: break-word;
        overflow-wrap: break-word;
        white-space: normal;
        max-width: 100%;
        min-height: 80px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #fff;
        word-break: break-word;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .metric-label {
        font-size: 14px;
        color: #d1d5db;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .header {
        border-bottom: 1px solid #2d3748;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    .violation {
        color: #ef4444;
        font-weight: bold;
    }
    .safe {
        color: #10b981;
        font-weight: bold;
    }
    .barclays-blue {
        color: #00aeef;
    }
</style>
""", unsafe_allow_html=True)

# TL;DR Section
st.markdown("""
### 📌 TL;DR
This project implements and backtests four trading strategies — **Momentum**, **Mean Reversion**, **Pair Trading**, and **Sentiment-based** — using macroeconomic, price, and text-based data (10-K filings).  
Each strategy generates dynamic signals, visualizations, and performance metrics (Sharpe, CAGR, Max Drawdown).  
The app supports historical + real-time updates.  
📊 [View Code & Methodology on GitHub](https://github.com/YOUR_GITHUB_REPO)
""")

# Author Footer and Contact Info
st.sidebar.markdown("### 👤 About the Author")
st.sidebar.markdown("""
**Siddhant Evre**  
Data/Quant Researcher  
📧 sevre2@illinois.edu  
🔗 [GitHub](https://github.com/YOUR_GITHUB_REPO)  
🗓️ Last Updated: July 1, 2025
""")

# Strategy Details Expander
with st.expander("🧠 Strategy Details & Assumptions"):
    st.markdown("""
- **Signal Frequency**: Daily  
- **Rebalancing**: Weekly  
- **Universe**: S&P 500  
- **Risk Management**: Equal-weighted, capped exposure per strategy  
- **Sentiment Source**: SEC 10-K filings via EDGAR  
- **Backtesting Period**: 2015–2024  
- **Slippage/Transaction Costs**: Not included (next step)

[Code on GitHub](https://github.com/YOUR_GITHUB_REPO)
""")

# Footer
st.divider()
st.caption("© 2025 Siddhant Evre | [GitHub](https://github.com/YOUR_GITHUB_REPO) | Last updated: July 1, 2025")

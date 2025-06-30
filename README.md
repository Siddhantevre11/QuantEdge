
# QuantEdge: Real-Time Alpha Signal Research Platform

🚀 **QuantEdge** is a real-time quant research platform built to generate, visualize, and backtest alpha signals from macroeconomic indicators, earnings sentiment, and equity factors. Designed for fast signal iteration and streamlined portfolio experimentation.

## 📌 Key Features

- 📈 **Alpha Signal Generation**
  - Ingests macroeconomic, earnings, and equity data
  - Extracts momentum, volatility, and valuation-based signals
  - Supports custom factor construction

- 🧪 **Factor Backtesting Engine**
  - Sharpe-optimized portfolio simulation
  - Signal performance metrics (IC, turnover, hit ratio, drawdown)
  - Long-short and market-neutral backtesting modes

- 🧠 **Real-Time Research Dashboard**
  - Built using Streamlit for fast UX
  - Displays alpha signals, PnL attribution, and rolling Sharpe ratios
  - Updated with live macro + equity feeds (via mocked pipelines)

## 📊 Demo

🔗 [Live App](https://quantedge-qvdwbvayy6kahujwdi55vw.streamlit.app/)

> ⚠️ Note: This public demo runs on mock data for confidentiality and performance. Proprietary datasets and signals can be integrated in a secure environment.

## 💡 Use Cases

- Rapid alpha signal prototyping for macro + equity strategies  
- Lightweight research assistant for quant PMs or junior analysts  
- Educational sandbox for exploring factor modeling and backtesting logic  

## ⚙️ Tech Stack

| Layer           | Tools Used                           |
|----------------|---------------------------------------|
| Frontend        | Streamlit, Plotly                     |
| Backend         | Python (Pandas, NumPy, Scikit-Learn) |
| Data Processing | Scheduled jobs (mocked), yfinance, FRED APIs |
| Deployment      | Streamlit Cloud, GitHub Actions       |

## 📁 Repo Structure


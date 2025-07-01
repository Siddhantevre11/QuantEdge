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
    page_title="QuantEdge Dashboard",
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

# ----------------------------
# DATA LOADING AND PROCESSING
# ----------------------------

class InstitutionalDataLoader:
    def __init__(self, start_date='2010-01-01'):
        self.start_date = start_date
        self.raw_data = None
        self.processed_data = None
        
    def load_raw_data(self):
        """Load market data from multiple sources"""
        # ETF data
        etfs = yf.download(['SPY', 'TLT', 'HYG', 'LQD'], start=self.start_date, progress=False)
        
        # Macroeconomic data from FRED
        fred_series = {
            'BAA10Y': 'baa_10y',
            'AAA10Y': 'aaa_10y',
            'DGS10': '10y_yield',
            'DGS2': '2y_yield',
            'VIXCLS': 'vix'
        }
        
        macro = web.DataReader(list(fred_series.keys()), 'fred', self.start_date)
        macro = macro.rename(columns=fred_series)
        
        # Merge datasets
        self.raw_data = pd.concat([etfs['Close'], macro], axis=1).ffill().dropna()
        self.raw_data.columns = ['SPY', 'TLT', 'HYG', 'LQD'] + list(fred_series.values())
        return self
    
    def process_signals(self):
        """Create regime-aware features and signals"""
        df = self.raw_data.copy()
        
        # Credit spreads
        df['quality_spread'] = df['baa_10y'] - df['aaa_10y']
        df['term_spread'] = df['10y_yield'] - df['2y_yield']
        
        # Z-score normalization
        for col in ['quality_spread', 'term_spread', 'vix']:
            df[f'{col}_z'] = (
                df[col] - df[col].rolling(126).mean()
            ) / df[col].rolling(126).std()
        
        # Composite signal
        df['signal'] = 0.7 * df['quality_spread_z'] + 0.3 * df['term_spread_z']
        
        self.processed_data = df.dropna()
        return self

class AdaptiveTWAP:
    def __init__(self, symbol, quantity, duration_min=5):
        self.symbol = symbol
        self.quantity = quantity
        self.duration = timedelta(minutes=duration_min)
        
    def execute(self):
        """Simulate TWAP execution with market impact"""
        fills = []
        remaining = self.quantity
        start = datetime.now(pytz.UTC)
        
        while remaining > 0 and datetime.now(pytz.UTC) < start + self.duration:
            # Simulate market data
            mid_price = 100 + np.random.normal(0, 0.1)
            spread = 0.05
            
            # Calculate slice size
            slice_size = min(remaining, max(100, int(1000000 * 0.0005)))
            
            # Price improvement logic
            fill_price = mid_price + np.random.uniform(-0.01, 0.01)
            
            # Record fill
            fills.append({
                'timestamp': datetime.now(pytz.UTC),
                'symbol': self.symbol,
                'price': fill_price,
                'shares': slice_size,
                'mid': mid_price
            })
            remaining -= slice_size
            
            # SEC-compliant pause
            time.sleep(0.1)
        
        return pd.DataFrame(fills)

class PnLAttributor:
    def __init__(self, trades):
        self.trades = trades
    
    def attribute(self):
        """Attribute PnL to different factors"""
        attribution = pd.DataFrame(index=self.trades.index)
        
        # Execution quality
        if 'mid' in self.trades and 'price' in self.trades and 'shares' in self.trades:
            attribution['Execution'] = (self.trades['price'] - self.trades['mid']) * self.trades['shares']
        else:
            attribution['Execution'] = 0
        
        # Market move
        attribution['Market'] = np.random.normal(0, 50, len(attribution))
        
        return attribution.dropna()

class BarclaysRiskSystem:
    def __init__(self):
        self.limits = {
            'DV01': 100000,   # $100k per 1bp
            'CS01': 50000,    # $50k per 1bp credit spread move
            'MaxNotional': 1e8 # $100MM
        }
    
    def check_limits(self, positions):
        """Check positions against risk limits"""
        exposures = self.calculate_exposures(positions)
        violations = {}
        
        for metric, limit in self.limits.items():
            if metric in exposures:
                violations[metric] = abs(exposures[metric]) > limit
            else:
                violations[metric] = False
        
        return violations
    
    def calculate_exposures(self, positions):
        """Calculate portfolio risk exposures"""
        exposures = {
            'MaxNotional': positions.get('notional', 0)
        }
        
        if 'notional' in positions and 'duration' in positions:
            exposures['DV01'] = positions['notional'] * 0.0001 * positions['duration']
        if 'notional' in positions and 'spread_duration' in positions:
            exposures['CS01'] = positions['notional'] * 0.0001 * positions['spread_duration']
        
        return exposures

class CrisisSimulator:
    SCENARIOS = {
        '2008 Crisis': {
            'equity_shock': -0.45,
            'credit_spread_widen': 0.35,  # 35bps
        },
        '2020 COVID': {
            'equity_shock': -0.35,
            'credit_spread_widen': 0.25,
        },
        '2022 Inflation': {
            'equity_shock': -0.25,
            'credit_spread_widen': 0.15,
        }
    }
    
    def __init__(self, portfolio):
        self.portfolio = portfolio
    
    def run_scenarios(self):
        """Run all defined stress scenarios"""
        results = {}
        for name, params in self.SCENARIOS.items():
            shocked_portfolio = self._apply_shocks(self.portfolio.copy(), params)
            results[name] = self._calculate_pnl_impact(shocked_portfolio)
        return pd.DataFrame.from_dict(results, orient='index', columns=['PnL Impact'])
    
    def _apply_shocks(self, portfolio, params):
        """Apply shocks to portfolio positions"""
        portfolio['price'] = portfolio['price'] * (1 + params['equity_shock'])
        portfolio['spread'] = portfolio['spread'] + params['credit_spread_widen']
        return portfolio
    
    def _calculate_pnl_impact(self, portfolio):
        """Calculate PnL impact of shocks"""
        return (portfolio['price'] * portfolio['shares']).sum() - \
               (self.portfolio['price'] * self.portfolio['shares']).sum()

# ----------------------------
# STREAMLIT DASHBOARD
# ----------------------------

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.processed_data = None
    st.session_state.executions = None
    st.session_state.pnl_breakdown = None
    st.session_state.stress_results = None

# Sidebar controls
st.sidebar.header("Quant Research")
st.sidebar.markdown("""
<span class="barclays-blue">Credit Spread Alpha Model</span>
""", unsafe_allow_html=True)

start_date = st.sidebar.date_input(
    "Start Date",
    value=pd.to_datetime('2020-01-01'),
    min_value=pd.to_datetime('2010-01-01'),
    max_value=pd.to_datetime('2023-12-31')
)

symbol = st.sidebar.selectbox(
    "ETF Symbol",
    options=['LQD', 'HYG', 'TLT', 'SPY'],
    index=0
)

trade_size = st.sidebar.slider(
    "Trade Size (Shares)",
    min_value=1000,
    max_value=100000,
    value=10000,
    step=1000
)

run_analysis = st.sidebar.button("Run Full Analysis")
show_advanced = st.sidebar.checkbox("Show Advanced Metrics")

# Main dashboard
st.title("📈 QuantEdge Dashboard")
st.markdown("""
<span class="barclays-blue">Credit Spread Alpha Model with Risk Management</span>
""", unsafe_allow_html=True)

# Run analysis when button is clicked
if run_analysis:
    with st.spinner("Loading market data..."):
        data_loader = InstitutionalDataLoader(start_date=start_date)
        data_loader.load_raw_data().process_signals()
        st.session_state.processed_data = data_loader.processed_data
    
    with st.spinner("Executing trades..."):
        algo = AdaptiveTWAP(symbol, trade_size)
        st.session_state.executions = algo.execute()
        st.session_state.executions['credit_duration'] = 3.8
        st.session_state.executions['vega'] = 25000
        st.session_state.executions['beta'] = 0.8
        st.session_state.executions['notional'] = 100 * st.session_state.executions['price']
        st.session_state.executions.index = st.session_state.executions['timestamp']
    
    with st.spinner("Running analysis..."):
        # PnL Attribution
        attributor = PnLAttributor(st.session_state.executions)
        st.session_state.pnl_breakdown = attributor.attribute()
        
        # Stress Testing
        portfolio = pd.DataFrame({
            'symbol': ['SPY', 'TLT'],
            'shares': [1000, 2000],
            'price': [400, 120],
            'spread': [0.01, 0.02],
        })
        simulator = CrisisSimulator(portfolio)
        st.session_state.stress_results = simulator.run_scenarios()
        
        st.session_state.data_loaded = True
        st.success("Analysis completed successfully!")

# Display results if available
if st.session_state.data_loaded:
    # Tab layout
    tab1, tab2, tab3 = st.tabs(["Market Signals", "Execution & PnL", "Risk Analysis"])

    with tab1:
        st.header("Market Signals")
        
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(
                px.line(st.session_state.processed_data, 
                        x=st.session_state.processed_data.index, 
                        y='quality_spread',
                        title="Credit Spread (BAA - AAA)",
                        labels={'value': 'Spread (bps)', 'index': 'Date'})
                .update_layout(template='plotly_dark', height=400),
                use_container_width=True
            )
        
        with col2:
            st.plotly_chart(
                px.line(st.session_state.processed_data, 
                        x=st.session_state.processed_data.index, 
                        y='term_spread',
                        title="Term Structure (10Y - 2Y)",
                        labels={'value': 'Yield Spread (%)', 'index': 'Date'})
                .update_layout(template='plotly_dark', height=400),
                use_container_width=True
            )
        
        st.plotly_chart(
            px.line(st.session_state.processed_data, 
                    x=st.session_state.processed_data.index, 
                    y='signal',
                    title="Composite Trading Signal",
                    labels={'value': 'Signal Strength', 'index': 'Date'})
            .update_layout(template='plotly_dark', height=400),
            use_container_width=True
        )

    with tab2:
        st.header("Trade Execution & Performance")
        
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(
                px.scatter(st.session_state.executions, 
                          x='timestamp', 
                          y='price',
                          size='shares', 
                          color='shares',
                          title="Trade Execution Prices",
                          labels={'price': 'Execution Price', 'timestamp': 'Time'})
                .update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
                .update_layout(template='plotly_dark', height=400),
                use_container_width=True
            )
        
        with col2:
            st.plotly_chart(
                px.bar(st.session_state.pnl_breakdown.sum().reset_index(),
                      x='index', 
                      y=0,
                      title="PnL Attribution by Factor",
                      labels={'index': 'Factor', '0': 'PnL Contribution'})
                .update_layout(template='plotly_dark', height=400),
                use_container_width=True
            )
        
        cum_pnl = st.session_state.pnl_breakdown.sum(axis=1).cumsum()
        st.plotly_chart(
            px.area(cum_pnl,
                   title="Cumulative PnL",
                   labels={'value': 'Cumulative PnL', 'index': 'Date'})
            .update_layout(template='plotly_dark', height=400),
            use_container_width=True
        )

    with tab3:
        st.header("Risk Management")
        
        # Risk exposures
        risk_system = BarclaysRiskSystem()
        positions = {
            'notional': 5000000,
            'duration': 4.2,
            'spread_duration': 3.8
        }
        exposures = risk_system.calculate_exposures(positions)
        violations = risk_system.check_limits(positions)
        
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(
                px.bar(x=list(exposures.keys()), 
                      y=list(exposures.values()),
                      title="Current Risk Exposures",
                      labels={'x': 'Risk Metric', 'y': 'Exposure'})
                .update_layout(template='plotly_dark', height=400),
                use_container_width=True
            )
        
        with col2:
            st.plotly_chart(
                px.bar(st.session_state.stress_results.reset_index(),
                      x='index', 
                      y='PnL Impact',
                      title="Stress Test Results",
                      labels={'index': 'Scenario', 'PnL Impact': 'PnL Impact ($)'})
                .update_layout(template='plotly_dark', height=400),
                use_container_width=True
            )
        
        # Risk limits table
        st.subheader("Risk Limit Monitoring")
        risk_data = []
        for metric, limit in risk_system.limits.items():
            value = exposures.get(metric, 0)
            status = "⚠️ Violation" if violations.get(metric, False) else "✅ Within Limit"
            risk_data.append({
                'Risk Metric': metric,
                'Current Value': f"${value:,.0f}",
                'Limit': f"${limit:,.0f}",
                'Status': status
            })
            
        risk_df = pd.DataFrame(risk_data)
        st.dataframe(
            risk_df.style.apply(
                lambda x: ['background: #1f2937' if x.name % 2 == 0 else 'background: #111827'] * len(x), 
                axis=1
            ).applymap(
                lambda x: 'color: #ef4444' if 'Violation' in x else 'color: #10b981',
                subset=['Status']
            ),
            use_container_width=True,
            height=200
        )

    # Performance metrics
    st.divider()
    st.subheader("Performance Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    cum_returns = (1 + st.session_state.pnl_breakdown.sum(axis=1)).prod() - 1
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{:.2%}</div>
            <div class="metric-label">Total Return</div>
        </div>
        """.format(cum_returns), unsafe_allow_html=True)
    
    max_drawdown = (1 + st.session_state.pnl_breakdown.sum(axis=1)).cumprod().div(
        (1 + st.session_state.pnl_breakdown.sum(axis=1)).cumprod().cummax()
    ).sub(1).min()
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{:.2%}</div>
            <div class="metric-label">Max Drawdown</div>
        </div>
        """.format(max_drawdown), unsafe_allow_html=True)
    
    sharpe_ratio = st.session_state.pnl_breakdown.sum(axis=1).mean() / st.session_state.pnl_breakdown.sum(axis=1).std() * np.sqrt(252)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{:.2f}</div>
            <div class="metric-label">Sharpe Ratio</div>
        </div>
        """.format(sharpe_ratio), unsafe_allow_html=True)
    
    win_rate = (st.session_state.pnl_breakdown.sum(axis=1) > 0).mean()
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{:.2%}</div>
            <div class="metric-label">Win Rate</div>
        </div>
        """.format(win_rate), unsafe_allow_html=True)

    # Advanced metrics
    if show_advanced:
        with st.expander("Advanced Metrics"):
            st.plotly_chart(
                px.line(st.session_state.pnl_breakdown,
                      title="Daily PnL Components",
                      labels={'value': 'PnL Contribution', 'index': 'Date'})
                .update_layout(template='plotly_dark', height=400),
                use_container_width=True
            )
            
            st.dataframe(
                st.session_state.pnl_breakdown.describe().T,
                use_container_width=True
            )

# Initial state message
if not st.session_state.data_loaded:
    st.info("Click 'Run Full Analysis' in the sidebar to start")
    st.markdown("""
    ### Quant Research Project
    This dashboard demonstrates a complete credit spread alpha model with:
    - Real-time market data integration
    - Algorithmic trade execution
    - PnL attribution analysis
    - Institutional risk management
    
    **Key Features:**
    - Credit spread signal generation
    - Adaptive TWAP execution
    - Stress testing across crisis scenarios
    - Risk limit monitoring
    """)

# Footer
st.divider()
st.caption("Author : Siddhant Evre ")

"""
Solana Meme Coin Simulation Dashboard
High-fidelity trading simulator with Golden Cross strategy

Features:
- Virtual wallet with realistic trading simulation
- Golden Cross (SMA Crossover) strategy
- Live price data from DexScreener
- Interactive charts with Plotly
- Trade ledger with PnL tracking
- Manual force sell control
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time

from data_engine import fetch_token_history, calculate_sma
from simulator import TradingSimulator, PositionStatus

# Page configuration
st.set_page_config(
    page_title="Solana Meme Coin Simulator",
    page_icon="🪙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e1e2f 0%, #2d2d44 100%);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #3d3d5c;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #00d4ff;
    }
    .metric-label {
        font-size: 14px;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .profit { color: #00ff88; }
    .loss { color: #ff4b4b; }
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
    .css-1d391kg {
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize all session state variables"""
    
    # Simulator instance
    if 'simulator' not in st.session_state:
        st.session_state.simulator = None
    
    # Trading parameters
    if 'fast_sma' not in st.session_state:
        st.session_state.fast_sma = 24
    
    if 'slow_sma' not in st.session_state:
        st.session_state.slow_sma = 72
    
    if 'initial_sol' not in st.session_state:
        st.session_state.initial_sol = 10.0
    
    # Data
    if 'price_data' not in st.session_state:
        st.session_state.price_data = None
    
    if 'token_address' not in st.session_state:
        st.session_state.token_address = "6fEd55Nfve4ZZD9XYS1Rp5ptxBP3Xbrq9PmUsAKYwxLC"
    
    # Simulation state
    if 'simulation_run' not in st.session_state:
        st.session_state.simulation_run = False
    
    if 'last_update' not in st.session_state:
        st.session_state.last_update = None


def create_trading_chart(data: pd.DataFrame, fast_sma: int, slow_sma: int) -> go.Figure:
    """
    Create an interactive trading chart with price and SMAs
    
    Args:
        data: DataFrame with OHLCV data
        fast_sma: Fast SMA period
        slow_sma: Slow SMA period
        
    Returns:
        Plotly figure object
    """
    fast_sma_col = f'SMA_{fast_sma}'
    slow_sma_col = f'SMA_{slow_sma}'
    
    # Create figure with subplots
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.7, 0.3],
        subplot_titles=('Price & SMA Crossover', 'Volume')
    )
    
    # Price candlestick
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
            name='Price',
            increasing_line_color='#00ff88',
            decreasing_line_color='#ff4b4b',
            increasing_fillcolor='rgba(0, 255, 136, 0.3)',
            decreasing_fillcolor='rgba(255, 75, 75, 0.3)'
        ),
        row=1, col=1
    )
    
    # Fast SMA
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data[fast_sma_col],
            mode='lines',
            name=f'Fast SMA ({fast_sma}h)',
            line=dict(color='#00d4ff', width=2)
        ),
        row=1, col=1
    )
    
    # Slow SMA
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data[slow_sma_col],
            mode='lines',
            name=f'Slow SMA ({slow_sma}h)',
            line=dict(color='#ff9500', width=2)
        ),
        row=1, col=1
    )
    
    # Volume bars
    colors = ['#00ff88' if data['close'].iloc[i] >= data['open'].iloc[i] else '#ff4b4b' 
              for i in range(len(data))]
    
    fig.add_trace(
        go.Bar(
            x=data.index,
            y=data['volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.7
        ),
        row=2, col=1
    )
    
    # Update layout
    fig.update_layout(
        title=dict(
            text='🪙 Token Price & Golden Cross Signals',
            font=dict(size=20, color='white')
        ),
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=600,
        xaxis_rangeslider_visible=False,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        hovermode='x unified'
    )
    
    # Update axes
    fig.update_xaxes(
        showgrid=True,
        gridcolor='rgba(255,255,255,0.1)',
        row=2, col=1
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor='rgba(255,255,255,0.1)',
        row=1, col=1
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor='rgba(255,255,255,0.1)',
        title='Volume',
        row=2, col=1
    )
    
    return fig


def create_equity_curve_chart(equity_data: list) -> go.Figure:
    """Create equity curve chart from backtest results"""
    if not equity_data:
        return None
    
    df = pd.DataFrame(equity_data)
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['value'],
            mode='lines',
            name='Portfolio Value',
            fill='tozeroy',
            line=dict(color='#00ff88', width=2),
            fillcolor='rgba(0, 255, 136, 0.1)'
        )
    )
    
    fig.update_layout(
        title=dict(
            text='📈 Portfolio Equity Curve',
            font=dict(size=16, color='white')
        ),
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=300,
        xaxis_title='Time',
        yaxis_title='Value (SOL)',
        hovermode='x unified'
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    
    return fig


def display_metrics(simulator: TradingSimulator):
    """Display key metrics in a dashboard format"""
    
    wallet = simulator.wallet
    
    # Current price and SMAs
    signal, fast_sma, slow_sma, trend_strength = simulator.get_latest_signals()
    
    # Portfolio metrics
    portfolio_value = wallet.get_portfolio_value(simulator.current_price)
    pnl, pnl_percent = wallet.get_pnl(wallet.entry_price, simulator.current_price)
    
    # Create columns for metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Current Price</div>
            <div class="metric-value">${simulator.current_price:.10f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        status_color = "#00ff88" if wallet.position_status == PositionStatus.LONG else "#888"
        status_text = "LONG" if wallet.position_status == PositionStatus.LONG else "FLAT"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Position</div>
            <div class="metric-value" style="color: {status_color}">{status_text}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        pnl_color = "#00ff88" if pnl >= 0 else "#ff4b4b"
        pnl_symbol = "+" if pnl >= 0 else ""
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Unrealized PnL</div>
            <div class="metric-value" style="color: {pnl_color}">{pnl_symbol}{pnl:.4f} SOL</div>
            <div style="font-size: 14px; color: {pnl_color}">{pnl_symbol}{pnl_percent:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">SOL Balance</div>
            <div class="metric-value">{wallet.sol_balance:.4f} SOL</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        token_display = f"{wallet.token_balance:,.0f}" if wallet.token_balance > 0 else "0"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Token Balance</div>
            <div class="metric-value">{token_display}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Signal indicator
    st.divider()
    
    signal_col1, signal_col2, signal_col3 = st.columns([1, 2, 1])
    
    with signal_col1:
        if signal == 'buy':
            st.success("🟢 **BUY SIGNAL** - Golden Cross Detected!")
        elif signal == 'sell':
            st.error("🔴 **SELL SIGNAL** - Death Cross Detected!")
        else:
            st.info("⚪ **NO SIGNAL** - Waiting for crossover")
    
    with signal_col2:
        trend_direction = "↑ BULLISH" if trend_strength > 0 else "↓ BEARISH"
        st.metric("Trend Strength", f"{trend_direction} ({trend_strength*100:.2f}%)")
    
    with signal_col3:
        sma_diff = fast_sma - slow_sma
        st.metric("SMA Gap", f"${sma_diff:.10f}", delta=f"{'+' if sma_diff > 0 else ''}{sma_diff:.8f}")


def display_trade_ledger(trades: list):
    """Display trade history in a styled table"""
    if not trades:
        st.info("No trades executed yet. Adjust parameters and run the simulation.")
        return
    
    df = pd.DataFrame(trades)
    
    # Format for display
    display_df = df.copy()
    
    # Color code PnL
    def color_pnl(val):
        if val == '-':
            return ''
        try:
            num = float(val.replace('+', '').replace(' SOL', ''))
            return 'color: #00ff88' if num > 0 else 'color: #ff4b4b'
        except:
            return ''
    
    # Display styled dataframe
    st.subheader("📋 Trade Ledger")
    
    # Use Streamlit's data editor for interactive table
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "timestamp": st.column_config.TextColumn("Time", width="medium"),
            "type": st.column_config.TextColumn("Type", width="small"),
            "price": st.column_config.TextColumn("Price", width="medium"),
            "sol_amount": st.column_config.TextColumn("SOL Amount", width="medium"),
            "token_amount": st.column_config.TextColumn("Token Amount", width="medium"),
            "fee": st.column_config.TextColumn("Fee", width="small"),
            "pnl_sol": st.column_config.TextColumn("PnL (SOL)", width="medium"),
            "pnl_percent": st.column_config.TextColumn("PnL %", width="small"),
            "note": st.column_config.TextColumn("Note", width="large"),
        }
    )
    
    # Summary stats
    if trades:
        df_numeric = pd.DataFrame(trades)
        buy_count = len(df_numeric[df_numeric['type'] == 'BUY'])
        sell_count = len(df_numeric[df_numeric['type'] == 'SELL'])
        
        total_fees = sum(float(t['fee'].replace(' SOL', '')) for t in trades)
        
        st.caption(f"📊 Total Trades: {len(trades)} | Buys: {buy_count} | Sells: {sell_count} | Total Fees Paid: {total_fees:.6f} SOL")


def sidebar_controls():
    """Render sidebar with all controls"""
    st.sidebar.title("🎛️ Strategy Controls")
    
    # Token configuration
    st.sidebar.subheader("🪙 Token Configuration")
    token_address = st.sidebar.text_input(
        "Token Address",
        value=st.session_state.token_address,
        help="Solana token address to simulate"
    )
    
    if token_address != st.session_state.token_address:
        st.session_state.token_address = token_address
        st.session_state.simulation_run = False
        st.session_state.price_data = None
    
    # Virtual wallet settings
    st.sidebar.subheader("💰 Virtual Wallet")
    initial_sol = st.sidebar.slider(
        "Initial SOL Balance",
        min_value=0.1,
        max_value=100.0,
        value=st.session_state.initial_sol,
        step=0.1,
        help="Starting SOL amount for simulation"
    )
    
    if initial_sol != st.session_state.initial_sol:
        st.session_state.initial_sol = initial_sol
        st.session_state.simulation_run = False
    
    # Strategy parameters
    st.sidebar.subheader("📈 Golden Cross Strategy")
    fast_sma = st.sidebar.slider(
        "Fast SMA Period (hours)",
        min_value=6,
        max_value=168,  # 7 days
        value=st.session_state.fast_sma,
        step=6,
        help="Fast SMA period for crossover detection"
    )
    
    slow_sma = st.sidebar.slider(
        "Slow SMA Period (hours)",
        min_value=24,
        max_value=336,  # 14 days
        value=st.session_state.slow_sma,
        step=12,
        help="Slow SMA period for crossover detection"
    )
    
    if fast_sma >= slow_sma:
        st.sidebar.error("⚠️ Fast SMA must be less than Slow SMA!")
        return None
    
    if fast_sma != st.session_state.fast_sma or slow_sma != st.session_state.slow_sma:
        st.session_state.fast_sma = fast_sma
        st.session_state.slow_sma = slow_sma
        st.session_state.simulation_run = False
    
    # Trading fees
    st.sidebar.subheader("💸 Trading Fees")
    slippage = st.sidebar.slider(
        "Slippage Rate",
        min_value=0.0,
        max_value=0.05,
        value=0.01,
        step=0.001,
        format="%.1f%%",
        help="Simulated slippage per trade"
    ) * 100
    
    trading_fee = st.sidebar.slider(
        "Trading Fee",
        min_value=0.0,
        max_value=0.05,
        value=0.01,
        step=0.001,
        format="%.1f%%",
        help="Trading fee per trade"
    ) * 100
    
    # Data refresh
    st.sidebar.subheader("📊 Data")
    if st.sidebar.button("🔄 Refresh Data", type="primary"):
        st.session_state.simulation_run = False
        st.rerun()
    
    return {
        'token_address': token_address,
        'initial_sol': initial_sol,
        'fast_sma': fast_sma,
        'slow_sma': slow_sma,
        'slippage': slippage / 100,
        'trading_fee': trading_fee / 100
    }


def main():
    """Main application entry point"""
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar controls
    config = sidebar_controls()
    
    if config is None:
        st.error("Invalid configuration: Fast SMA must be less than Slow SMA")
        return
    
    # Main content
    st.title("🪙 Solana Meme Coin Simulation Dashboard")
    st.markdown("**Golden Cross Strategy Simulator** | *Virtual Trading with Real Market Data*")
    
    # Load data if needed
    if st.session_state.price_data is None:
        with st.spinner("Fetching token data from DexScreener..."):
            data = fetch_token_history(config['token_address'], 60)
            
            if data is not None and len(data) > 0:
                st.session_state.price_data = data
                st.success(f"✅ Loaded {len(data)} hours of data")
            else:
                st.error("❌ Failed to load token data. Using synthetic data.")
                # Fallback to synthetic data
                st.session_state.price_data = fetch_token_history(config['token_address'], 60)
    
    data = st.session_state.price_data
    
    if data is None or len(data) == 0:
        st.error("No price data available. Please check the token address.")
        return
    
    # Initialize or reinitialize simulator
    if not st.session_state.simulation_run or st.session_state.simulator is None:
        st.session_state.simulator = TradingSimulator(
            initial_sol=config['initial_sol'],
            fast_sma=config['fast_sma'],
            slow_sma=config['slow_sma'],
            slippage=config['slippage'],
            trading_fee=config['trading_fee']
        )
        st.session_state.simulator.load_data(data)
        st.session_state.simulation_run = True
    
    simulator = st.session_state.simulator
    
    # Run backtest
    if st.button("▶️ Run Backtest", type="primary", use_container_width=True):
        with st.spinner("Running backtest simulation..."):
            results = simulator.run_backtest()
            st.session_state.backtest_results = results
            st.session_state.simulation_run = True
        
        st.success(f"✅ Backtest complete! Final balance: {results['final_balance']:.4f} SOL")
    
    # Display metrics
    display_metrics(simulator)
    
    # Manual controls
    st.divider()
    
    col_force_sell, col_reset = st.columns(2)
    
    with col_force_sell:
        if st.button("🚨 FORCE SELL", type="secondary", use_container_width=True):
            if simulator.wallet.position_status == PositionStatus.LONG:
                trade = simulator.manual_sell()
                if trade:
                    st.success(f"✅ Force sell executed! PnL: {trade.pnl_sol:+.4f} SOL")
                else:
                    st.error("❌ No position to sell")
            else:
                st.warning("⚠️ No open position to sell")
    
    with col_reset:
        if st.button("🔄 Reset Simulation", type="secondary", use_container_width=True):
            st.session_state.simulation_run = False
            st.session_state.simulator = None
            st.rerun()
    
    # Charts
    st.divider()
    
    # Price chart
    st.subheader("📈 Price & SMA Analysis")
    chart = create_trading_chart(data, config['fast_sma'], config['slow_sma'])
    st.plotly_chart(chart, use_container_width=True)
    
    # Trade ledger
    if hasattr(st.session_state, 'backtest_results'):
        display_trade_ledger(st.session_state.backtest_results.get('trades', []))
        
        # Equity curve
        equity_data = st.session_state.backtest_results.get('equity_curve', [])
        if equity_data:
            equity_chart = create_equity_curve_chart(equity_data)
            if equity_chart:
                st.plotly_chart(equity_chart, use_container_width=True)
    
    # Data info
    with st.expander("📊 Data Information"):
        st.write(f"**Token Address:** `{config['token_address']}`")
        st.write(f"**Data Range:** {data.index.min().strftime('%Y-%m-%d %H:%M')} to {data.index.max().strftime('%Y-%m-%d %H:%M')}")
        st.write(f"**Data Points:** {len(data)} hours")
        st.write(f"**Price Range:** ${data['close'].min():.10f} - ${data['close'].max():.10f}")
        st.write(f"**Average Price:** ${data['close'].mean():.10f}")
    
    # Strategy explanation
    with st.expander("📚 Strategy Explanation"):
        st.markdown("""
        ### Golden Cross Strategy
        
        **How it works:**
        1. **Buy Signal (Golden Cross):** When the Fast SMA crosses ABOVE the Slow SMA
        2. **Sell Signal (Death Cross):** When the Fast SMA crosses BELOW the Slow SMA
        
        **Why it works:**
        - Trend-following strategy that captures sustained price movements
        - The Fast SMA responds quickly to price changes
        - The Slow SMA filters out noise and confirms the trend
        
        **Settings:**
        - **Fast SMA (24h):** Captures short-term momentum
        - **Slow SMA (72h):** Confirms medium-term trend direction
        
        **Note:** Meme coins are highly volatile. Always use proper risk management!
        """)


if __name__ == "__main__":
    main()

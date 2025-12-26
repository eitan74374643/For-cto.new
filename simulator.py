"""
Virtual Wallet and Trading Simulator for Solana Meme Coin Strategy
Implements Golden Cross (SMA Crossover) trading strategy with realistic simulation
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradeType(Enum):
    BUY = "BUY"
    SELL = "SELL"


class PositionStatus(Enum):
    FLAT = "FLAT"
    LONG = "LONG"


@dataclass
class Trade:
    """Represents a simulated trade"""
    timestamp: datetime
    trade_type: TradeType
    price: float
    amount_sol: float
    amount_token: float
    fee_sol: float
    slippage: float
    total_cost: float
    pnl_sol: float = 0.0
    pnl_percent: float = 0.0
    note: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M"),
            "type": self.trade_type.value,
            "price": f"${self.price:.10f}",
            "sol_amount": f"{self.amount_sol:.4f}",
            "token_amount": f"{self.amount_token:,.0f}",
            "fee": f"{self.fee_sol:.6f}",
            "slippage": f"{self.slippage:.2%}",
            "pnl_sol": f"{self.pnl_sol:+.4f}" if self.pnl_sol != 0 else "-",
            "pnl_percent": f"{self.pnl_percent:+.2f}%" if self.pnl_percent != 0 else "-",
            "note": self.note
        }


@dataclass
class VirtualWallet:
    """
    Virtual wallet for simulating crypto trading
    Tracks balance, positions, and trade history
    """
    initial_sol: float
    slippage_rate: float = 0.01  # 1% slippage per trade
    trading_fee: float = 0.01     # 1% trading fee per trade
    
    # State
    sol_balance: float = field(init=False)
    token_balance: float = field(init=False)
    position_status: PositionStatus = field(init=False)
    trades: List[Trade] = field(init=False, default_factory=list)
    entry_price: float = field(init=False, default=0.0)
    
    def __post_init__(self):
        self.sol_balance = self.initial_sol
        self.token_balance = 0.0
        self.position_status = PositionStatus.FLAT
        self.entry_price = 0.0
    
    @property
    def total_value(self) -> float:
        """Calculate total portfolio value in SOL at current price"""
        if self.position_status == PositionStatus.LONG:
            # This will be set dynamically with current price
            return self.sol_balance  # Placeholder
        return self.sol_balance
    
    def calculate_fees(self, sol_amount: float) -> Tuple[float, float]:
        """Calculate slippage and trading fees"""
        slippage_cost = sol_amount * self.slippage_rate
        trading_fee = sol_amount * self.trading_fee
        return slippage_cost, trading_fee
    
    def execute_buy(self, current_price: float, sol_amount: float, 
                   timestamp: datetime, note: str = "") -> Trade:
        """
        Execute a simulated BUY order
        
        Args:
            current_price: Current token price in SOL
            sol_amount: Amount of SOL to spend
            timestamp: Current timestamp
            note: Optional note for the trade
            
        Returns:
            Trade object with execution details
        """
        if self.sol_balance < sol_amount:
            logger.warning(f"Insufficient SOL balance: {self.sol_balance}")
            sol_amount = self.sol_balance  # Use all available
        
        if sol_amount < 0.0001:
            raise ValueError("SOL amount too small for trade")
        
        # Calculate fees
        slippage_cost, trading_fee = self.calculate_fees(sol_amount)
        total_cost = sol_amount + slippage_cost + trading_fee
        
        if total_cost > self.sol_balance:
            sol_amount = self.sol_balance - slippage_cost - trading_fee
            total_cost = self.sol_balance
        
        # Calculate tokens received (after fees)
        effective_price = current_price * (1 + self.slippage_rate)
        token_amount = sol_amount / effective_price
        
        # Execute trade
        self.sol_balance -= total_cost
        self.token_balance += token_amount
        self.position_status = PositionStatus.LONG
        self.entry_price = current_price
        
        # Create trade record
        trade = Trade(
            timestamp=timestamp,
            trade_type=TradeType.BUY,
            price=current_price,
            amount_sol=sol_amount,
            amount_token=token_amount,
            fee_sol=trading_fee,
            slippage=self.slippage_rate,
            total_cost=total_cost,
            note=note
        )
        
        self.trades.append(trade)
        logger.info(f"BUY: {sol_amount:.4f} SOL -> {token_amount:,.0f} tokens at ${current_price:.10f}")
        
        return trade
    
    def execute_sell(self, current_price: float, timestamp: datetime, 
                    note: str = "", force: bool = False) -> Optional[Trade]:
        """
        Execute a simulated SELL order
        
        Args:
            current_price: Current token price in SOL
            timestamp: Current timestamp
            note: Optional note for the trade
            force: If True, sell entire position regardless of strategy
            
        Returns:
            Trade object with execution details, or None if no position
        """
        if self.position_status != PositionStatus.LONG or self.token_balance <= 0:
            logger.warning("No position to sell")
            return None
        
        # Calculate sell amount (all tokens or partial)
        token_amount = self.token_balance if force else self.token_amount_from_strategy()
        token_amount = min(token_amount, self.token_balance)
        
        if token_amount < 1:
            logger.warning(f"Token amount too small: {token_amount}")
            return None
        
        # Calculate proceeds
        effective_price = current_price * (1 - self.slippage_rate)
        gross_proceeds = token_amount * effective_price
        
        # Calculate fees
        slippage_cost = (token_amount * current_price) * self.slippage_rate
        trading_fee = gross_proceeds * self.trading_fee
        total_fee = slippage_cost + trading_fee
        
        net_proceeds = gross_proceeds - trading_fee
        
        # Calculate PnL
        cost_basis = token_amount * self.entry_price
        pnl = net_proceeds - cost_basis
        pnl_percent = (pnl / cost_basis) * 100 if cost_basis > 0 else 0
        
        # Execute trade
        self.sol_balance += net_proceeds
        self.token_balance -= token_amount
        
        # Update position status
        if self.token_balance < 1:  # Dust left, consider it closed
            self.token_balance = 0
            self.position_status = PositionStatus.FLAT
        
        # Create trade record
        trade = Trade(
            timestamp=timestamp,
            trade_type=TradeType.SELL,
            price=current_price,
            amount_sol=net_proceeds,
            amount_token=token_amount,
            fee_sol=trading_fee,
            slippage=self.slippage_rate,
            total_cost=net_proceeds,
            pnl_sol=pnl,
            pnl_percent=pnl_percent,
            note=note
        )
        
        self.trades.append(trade)
        logger.info(f"SELL: {token_amount:,.0f} tokens -> {net_proceeds:.4f} SOL at ${current_price:.10f} | PnL: {pnl:+.4f} SOL ({pnl_percent:+.2f}%)")
        
        return trade
    
    def token_amount_from_strategy(self) -> float:
        """Determine how many tokens to sell based on strategy (can be customized)"""
        return self.token_balance  # Default: sell all
    
    def get_portfolio_value(self, current_price: float) -> float:
        """Calculate total portfolio value at given price"""
        token_value = self.token_balance * current_price
        return self.sol_balance + token_value
    
    def get_pnl(self, entry_price: float, current_price: float) -> Tuple[float, float]:
        """Calculate unrealized PnL"""
        if self.position_status != PositionStatus.LONG:
            return 0.0, 0.0
        
        token_value = self.token_balance * current_price
        cost_basis = self.token_balance * entry_price
        pnl = token_value - cost_basis
        pnl_percent = (pnl / cost_basis) * 100 if cost_basis > 0 else 0
        
        return pnl, pnl_percent


class GoldenCrossStrategy:
    """
    Golden Cross Strategy using SMA crossovers
    
    Buy Signal: Fast SMA crosses ABOVE Slow SMA
    Sell Signal: Fast SMA crosses BELOW Slow SMA
    
    This is a momentum-based trend-following strategy
    """
    
    def __init__(self, fast_sma_period: int, slow_sma_period: int):
        """
        Initialize strategy
        
        Args:
            fast_sma_period: Period for fast SMA (in hours, e.g., 24)
            slow_sma_period: Period for slow SMA (in hours, e.g., 72)
        """
        self.fast_sma_period = fast_sma_period
        self.slow_sma_period = slow_sma_period
        
        # State tracking
        self.last_signal = None  # 'buy', 'sell', or None
        self.position_open = False
    
    def calculate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate trading signals based on SMA crossovers
        
        Args:
            data: DataFrame with 'close' prices and SMA columns
            
        Returns:
            DataFrame with 'signal' column
        """
        df = data.copy()
        
        # Ensure SMA columns exist
        fast_col = f'SMA_{self.fast_sma_period}'
        slow_col = f'SMA_{self.slow_sma_period}'
        
        if fast_col not in df.columns or slow_col not in df.columns:
            raise ValueError(f"Required SMA columns not found: {fast_col}, {slow_col}")
        
        # Calculate crossover signals
        df['signal'] = 0  # 0 = no signal, 1 = buy, -1 = sell
        
        # Golden Cross: Fast SMA crosses above Slow SMA
        golden_cross = (df[fast_col] > df[slow_col]) & (df[fast_col].shift(1) <= df[slow_col].shift(1))
        df.loc[golden_cross, 'signal'] = 1
        
        # Death Cross: Fast SMA crosses below Slow SMA
        death_cross = (df[fast_col] < df[slow_col]) & (df[fast_col].shift(1) >= df[slow_col].shift(1))
        df.loc[death_cross, 'signal'] = -1
        
        # Calculate trend strength
        df['trend_strength'] = (df[fast_col] - df[slow_col]) / df[slow_col]
        
        return df
    
    def get_latest_signal(self, data: pd.DataFrame) -> Tuple[Optional[str], float]:
        """
        Get the latest trading signal and trend strength
        
        Returns:
            Tuple of (signal, trend_strength)
        """
        if len(data) < 2:
            return None, 0.0
        
        df = self.calculate_signals(data)
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Check for new signals
        signal = None
        if latest['signal'] == 1 and prev['signal'] != 1:
            signal = 'buy'
        elif latest['signal'] == -1 and prev['signal'] != -1:
            signal = 'sell'
        
        trend_strength = latest['trend_strength']
        
        return signal, trend_strength
    
    def should_buy(self, data: pd.DataFrame) -> bool:
        """Check if we should enter a position"""
        signal, _ = self.get_latest_signal(data)
        return signal == 'buy' and not self.position_open
    
    def should_sell(self, data: pd.DataFrame) -> bool:
        """Check if we should exit a position"""
        signal, _ = self.get_latest_signal(data)
        return signal == 'sell' and self.position_open


class TradingSimulator:
    """
    Main simulator that combines wallet and strategy
    """
    
    def __init__(self, initial_sol: float, fast_sma: int, slow_sma: int,
                 slippage: float = 0.01, trading_fee: float = 0.01):
        self.wallet = VirtualWallet(
            initial_sol=initial_sol,
            slippage_rate=slippage,
            trading_fee=trading_fee
        )
        self.strategy = GoldenCrossStrategy(fast_sma, slow_sma)
        self.data = None
        self.current_price = 0.0
    
    def load_data(self, data: pd.DataFrame):
        """Load price data and calculate SMAs"""
        self.data = data.copy()
        
        # Calculate SMAs
        fast_sma_col = f'SMA_{self.strategy.fast_sma_period}'
        slow_sma_col = f'SMA_{self.strategy.slow_sma_period}'
        
        self.data[fast_sma_col] = self.data['close'].rolling(
            window=self.strategy.fast_sma_period
        ).mean()
        
        self.data[slow_sma_col] = self.data['close'].rolling(
            window=self.strategy.slow_sma_period
        ).mean()
        
        # Get current price
        self.current_price = self.data.iloc[-1]['close']
    
    def run_backtest(self) -> Dict:
        """
        Run a complete backtest on the historical data
        
        Returns:
            Dictionary with backtest results
        """
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")
        
        results = {
            'initial_balance': self.wallet.initial_sol,
            'final_balance': 0,
            'total_pnl': 0,
            'total_pnl_percent': 0,
            'num_trades': 0,
            'num_buys': 0,
            'num_sells': 0,
            'win_rate': 0,
            'trades': [],
            'equity_curve': []
        }
        
        initial_balance = self.wallet.initial_sol
        
        # Calculate signals for entire dataset
        df = self.strategy.calculate_signals(self.data)
        
        for i in range(len(df)):
            row = df.iloc[i]
            price = row['close']
            signal = row['signal']
            timestamp = df.index[i]
            
            # Execute trades based on signals
            if signal == 1:  # Buy signal
                if self.wallet.position_status != PositionStatus.LONG:
                    trade = self.wallet.execute_buy(
                        current_price=price,
                        sol_amount=self.wallet.sol_balance,  # Use all available
                        timestamp=timestamp,
                        note=f"Golden Cross Buy (Fast SMA > Slow SMA)"
                    )
                    self.strategy.position_open = True
                    results['num_buys'] += 1
            
            elif signal == -1:  # Sell signal
                if self.wallet.position_status == PositionStatus.LONG:
                    trade = self.wallet.execute_sell(
                        current_price=price,
                        timestamp=timestamp,
                        note=f"Death Cross Sell (Fast SMA < Slow SMA)"
                    )
                    if trade:
                        self.strategy.position_open = False
                        results['num_sells'] += 1
            
            # Record equity
            portfolio_value = self.wallet.get_portfolio_value(price)
            results['equity_curve'].append({
                'timestamp': timestamp,
                'value': portfolio_value
            })
        
        # Close any remaining position at final price
        if self.wallet.position_status == PositionStatus.LONG:
            final_trade = self.wallet.execute_sell(
                current_price=self.current_price,
                timestamp=df.index[-1],
                note="Final position close",
                force=True
            )
            if final_trade:
                results['num_sells'] += 1
        
        # Calculate final metrics
        results['final_balance'] = self.wallet.sol_balance
        results['total_pnl'] = self.wallet.sol_balance - initial_balance
        results['total_pnl_percent'] = (
            (results['total_pnl'] / initial_balance) * 100
        )
        results['num_trades'] = len(self.wallet.trades)
        results['trades'] = [t.to_dict() for t in self.wallet.trades]
        
        # Calculate win rate
        sell_trades = [t for t in self.wallet.trades if t.trade_type == TradeType.SELL]
        winning_trades = sum(1 for t in sell_trades if t.pnl_sol > 0)
        results['win_rate'] = (
            (winning_trades / len(sell_trades) * 100) if sell_trades else 0
        )
        
        return results
    
    def get_latest_signals(self) -> Tuple[Optional[str], float, float, float]:
        """Get current market state and signals"""
        if self.data is None:
            return None, 0, 0, 0
        
        latest = self.data.iloc[-1]
        fast_sma = f'SMA_{self.strategy.fast_sma_period}'
        slow_sma = f'SMA_{self.strategy.slow_sma_period}'
        
        fast_value = latest[fast_sma] if fast_sma in latest else 0
        slow_value = latest[slow_sma] if slow_sma in latest else 0
        
        signal, trend_strength = self.strategy.get_latest_signal(self.data)
        
        return signal, fast_value, slow_value, trend_strength
    
    def manual_sell(self) -> Optional[Trade]:
        """Execute a manual sell at current price"""
        if self.wallet.position_status != PositionStatus.LONG:
            return None
        
        trade = self.wallet.execute_sell(
            current_price=self.current_price,
            timestamp=datetime.now(),
            note="Manual Force Sell",
            force=True
        )
        
        if trade:
            self.strategy.position_open = False
        
        return trade


if __name__ == "__main__":
    # Quick test of the simulator
    from data_engine import fetch_token_history, calculate_sma
    
    token_address = "6fEd55Nfve4ZZD9XYS1Rp5ptxBP3Xbrq9PmUsAKYwxLC"
    
    print("Loading data...")
    data = fetch_token_history(token_address, 60)
    
    if data is not None:
        print(f"Loaded {len(data)} data points")
        print(f"Price range: ${data['close'].min():.10f} - ${data['close'].max():.10f}")
        
        # Initialize simulator
        sim = TradingSimulator(
            initial_sol=10.0,
            fast_sma=24,
            slow_sma=72
        )
        
        sim.load_data(data)
        
        # Run backtest
        results = sim.run_backtest()
        
        print("\n=== Backtest Results ===")
        print(f"Initial Balance: {results['initial_balance']:.4f} SOL")
        print(f"Final Balance: {results['final_balance']:.4f} SOL")
        print(f"Total PnL: {results['total_pnl']:+.4f} SOL ({results['total_pnl_percent']:+.2f}%)")
        print(f"Number of Trades: {results['num_trades']}")
        print(f"Win Rate: {results['win_rate']:.1f}%")

#===== backtest.py =====#

import numpy as np
import pandas as pd

def backtest_pair(
    series1, series2, signals, beta, 
    capital_base=1_000_000, 
    risk_aversion=1.0,
    slippage_pct=0.0005,               # 5 bps slippage (0.05%)
    transaction_cost_pct=0.001         # 10 bps cost (0.10%)
):
    """
    Backtest a mean-reversion strategy with dynamic position sizing and realistic execution costs.

    Args:
        series1 (pd.Series): Price series of asset A
        series2 (pd.Series): Price series of asset B
        signals (pd.Series): 1 = long spread, -1 = short spread, 0 = neutral
        beta (float): Hedge ratio
        capital_base (float): Starting capital in USD
        risk_aversion (float): Higher = smaller positions
        slippage_pct (float): Slippage applied on each trade (%)
        transaction_cost_pct (float): Transaction cost per trade (%)

    Returns:
        pd.DataFrame: Includes spread, signals, exposure, capital, and execution-aware PnL
    """
    # Align signals to index
    signals = signals[-len(series1):]
    signals = signals.reindex(series1.index)

    # Spread = A - beta * B
    spread = series1 - beta * series2
    spread_returns = spread.diff()

    # Rolling stats and z-score
    spread_mean = spread.rolling(20).mean()
    spread_std = spread.rolling(20).std()
    zscore = (spread - spread_mean) / (spread_std + 1e-6)
    zscore.fillna(0, inplace=True)

    # Position size ∝ |zscore| / volatility (scaled by risk_aversion)
    volatility = spread_std.bfill()
    position_size = (np.abs(zscore) / (volatility + 1e-6)) / risk_aversion
    position_size = position_size.clip(upper=2.0)

    # Exposure = size × direction
    directional_exposure = position_size * signals

    # Detect trades
    trade_indicator = directional_exposure.diff().fillna(0) != 0

    # Execution costs per trade: slippage + transaction cost
    execution_cost = trade_indicator.astype(float) * (
        np.abs(directional_exposure) * (slippage_pct + transaction_cost_pct)
    )

    # PnL = Previous exposure × Δspread - execution costs
    pnl = directional_exposure.shift().fillna(0) * spread_returns - execution_cost
    capital = capital_base + pnl.cumsum()

    results = pd.DataFrame({
        "Spread": spread,
        "ZScore": zscore,
        "Signal": signals,
        "PositionSize": position_size,
        "Exposure": directional_exposure,
        "PnL": pnl,
        "Capital": capital
    })

    return results


def compute_metrics(results):
    """
    Compute key performance metrics from execution-aware results.
    """
    daily_returns = results["PnL"].dropna()
    cumulative = results["Capital"] if "Capital" in results else results["CumulativePnL"]
    
    sharpe = (
        daily_returns.mean() / daily_returns.std() * np.sqrt(252)
        if daily_returns.std() > 0 else 0
    )
    
    peak = cumulative.cummax()
    drawdown = peak - cumulative
    max_drawdown = drawdown.max()

    trades = results["Signal"].diff().fillna(0) != 0
    trade_count = trades.sum()

    wins = daily_returns[daily_returns > 0].count()
    total_trades = (results["Signal"].shift() != 0).sum()
    win_ratio = wins / total_trades if total_trades > 0 else 0

    return {
        "Sharpe Ratio": round(sharpe, 4),
        "Max Drawdown": round(max_drawdown, 4),
        "Win Ratio": round(win_ratio, 4),
        "Trade Count": int(trade_count)
    }

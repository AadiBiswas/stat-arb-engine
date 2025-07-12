import numpy as np
import pandas as pd

def backtest_pair(series1, series2, signals, beta):
    """
    Backtest a simple mean-reversion strategy on a cointegrated pair.

    Args:
        series1 (pd.Series): Price series of asset A
        series2 (pd.Series): Price series of asset B
        signals (pd.Series): Position signals: 1=long spread, -1=short spread, 0=neutral
        beta (float): Hedge ratio between A and B

    Returns:
        pd.DataFrame: Contains daily returns, cumulative returns, and signals
    """
    # Align signals to price data
    signals = signals[-len(series1):]  # trim if longer than prices
    signals = signals.reindex(series1.index)  # align to index

    # Spread = A - beta * B
    spread_position = signals

    # Daily PnL = Position_t-1 × ΔSpread
    spread = series1 - beta * series2
    spread_returns = spread.diff()

    pnl = spread_position.shift().fillna(0) * spread_returns
    cumulative_returns = pnl.cumsum()

    results = pd.DataFrame({
        "Spread": spread,
        "ZSignal": signals,
        "PnL": pnl,
        "CumulativePnL": cumulative_returns
    })

    return results
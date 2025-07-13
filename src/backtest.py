import numpy as np
import pandas as pd

def backtest_pair(series1, series2, signals, beta, capital_base=1_000_000, risk_aversion=1.0):
    """
    Backtest a mean-reversion strategy with dynamic position sizing.
    
    Args:
        series1 (pd.Series): Price series of asset A
        series2 (pd.Series): Price series of asset B
        signals (pd.Series): 1 = long spread, -1 = short spread, 0 = neutral
        beta (float): Hedge ratio
        capital_base (float): Starting capital in USD
        risk_aversion (float): Higher = smaller positions for same z-score
    
    Returns:
        pd.DataFrame: Results with spread, signals, PnL, capital, and sizing data
    """
    # Align signals to index
    signals = signals[-len(series1):]
    signals = signals.reindex(series1.index)

    # Build spread and daily change
    spread = series1 - beta * series2
    spread_returns = spread.diff()

    # Rolling statistics for volatility and z-score
    spread_mean = spread.rolling(20).mean()
    spread_std = spread.rolling(20).std()
    zscore = (spread - spread_mean) / spread_std
    zscore.fillna(0, inplace=True)

    # Position size ∝ |zscore| / volatility, adjusted by risk aversion
    volatility = spread_std.bfill()
    position_size = (np.abs(zscore) / (volatility + 1e-6)) / risk_aversion
    position_size = position_size.clip(upper=2.0)  # Max leverage = 2x capital

    # Directional exposure = position size × signal direction
    directional_exposure = position_size * signals

    # PnL = previous exposure × Δspread
    pnl = directional_exposure.shift().fillna(0) * spread_returns
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
    Compute common performance metrics from backtest results.
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

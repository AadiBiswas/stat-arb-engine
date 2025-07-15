import numpy as np
import pandas as pd

def backtest_pair(
    series1, series2, signals, beta, 
    capital_base=1_000_000, 
    risk_aversion=1.0,
    slippage_pct=0.0005,
    transaction_cost_pct=0.001,
    max_leverage=2.0,
    stop_loss_pct=None
):
    """
    Backtest a mean-reversion strategy with execution costs, leverage limits, and trade tagging.
    """
    signals = signals[-len(series1):]
    signals = signals.reindex(series1.index)

    spread = series1 - beta * series2
    spread_returns = spread.diff()

    spread_mean = spread.rolling(20).mean()
    spread_std = spread.rolling(20).std()
    zscore = (spread - spread_mean) / (spread_std + 1e-6)
    zscore.fillna(0, inplace=True)

    volatility = spread_std.bfill()
    raw_position = (np.abs(zscore) / (volatility + 1e-6)) / risk_aversion
    position_size = raw_position.clip(upper=max_leverage)

    exposure = position_size * signals
    capital = [capital_base]
    pnl_series = []
    event_tags = []

    for i in range(1, len(spread)):
        prev_expo = exposure.iloc[i - 1]
        curr_expo = exposure.iloc[i]
        delta_expo = curr_expo - prev_expo

        cost = abs(delta_expo) * (slippage_pct + transaction_cost_pct)
        pnl = prev_expo * spread_returns.iloc[i] - cost
        new_capital = capital[-1] + pnl

        if prev_expo == 0 and curr_expo != 0:
            tag = "Entry"
        elif prev_expo != 0 and curr_expo == 0:
            tag = "Exit"
        elif stop_loss_pct and (pnl < -stop_loss_pct * capital[-1]):
            tag = "StopLoss"
        else:
            tag = None

        pnl_series.append(pnl)
        capital.append(new_capital)
        event_tags.append(tag)

    results = pd.DataFrame({
        "Spread": spread.iloc[1:],
        "ZScore": zscore.iloc[1:],
        "Signal": signals.iloc[1:],
        "PositionSize": position_size.iloc[1:],
        "Exposure": exposure.iloc[1:],
        "PnL": pnl_series,
        "Capital": capital[1:],
        "Event": event_tags
    })

    # Ensure datetime index is preserved
    if isinstance(series1.index, pd.DatetimeIndex):
        results.index = series1.index[1:]
    return results


def compute_metrics(results):

    """
    Compute performance metrics from backtest results.
    """
    daily_returns = results["PnL"].dropna()
    cumulative = results["Capital"].dropna()

    sharpe = (
        daily_returns.mean() / daily_returns.std() * np.sqrt(252)
        if daily_returns.std() > 0 else 0
    )

    peak = cumulative.cummax()
    drawdown = peak - cumulative
    max_drawdown = drawdown.max()

    trades = results["Event"].isin(["Entry", "Exit"])
    trade_count = trades.sum()

    wins = daily_returns[daily_returns > 0].count()
    total_trades = (results["Signal"].shift() != 0).sum()
    win_ratio = wins / total_trades if total_trades > 0 else 0

    initial_cap = cumulative.iloc[0]
    final_cap = cumulative.iloc[-1]

    # Robust: calculate actual duration in years if datetime index is available
    if isinstance(results.index, pd.DatetimeIndex):
        total_days = (results.index[-1] - results.index[0]).days
        years = total_days / 365.25 if total_days > 0 else 0
    else:
        # fallback to assuming 252 trading days/year
        years = len(cumulative) / 252

    total_return = (final_cap / initial_cap - 1) * 100
    cagr = ((final_cap / initial_cap) ** (1 / years) - 1) * 100 if years > 0 else 0

    exposure_days = (results["Exposure"].abs() > 0).sum()
    exposure_pct = exposure_days / len(results) * 100

    return {
        "Sharpe Ratio": round(sharpe, 4),
        "Max Drawdown": round(max_drawdown, 4),
        "Win Ratio": round(win_ratio, 4),
        "Trade Count": int(trade_count),
        "CAGR (%)": round(cagr, 2),
        "Total Return (%)": round(total_return, 2),
        "Exposure Time (%)": round(exposure_pct, 2)
    }


import argparse
import pandas as pd
from src.loader import download_prices
from src.coint import find_cointegrated_pairs
from src.strategy import compute_spread, generate_signals
from src.backtest import backtest_pair, compute_metrics
import matplotlib.pyplot as plt

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Statistical Arbitrage Backtest Runner")
    parser.add_argument("--capital", type=float, default=1_000_000, help="Initial capital base")
    parser.add_argument("--risk", type=float, default=1.0, help="Risk aversion (higher = smaller exposure)")
    parser.add_argument("--slippage", type=float, default=0.0005, help="Slippage as decimal (e.g. 0.001 = 10bps)")
    parser.add_argument("--txn_cost", type=float, default=0.001, help="Txn cost as decimal (e.g. 0.001 = 10bps)")
    parser.add_argument("--max_leverage", type=float, default=2.0, help="Maximum leverage (position size cap)")
    parser.add_argument("--stop_loss", type=float, default=None, help="Optional stop-loss as decimal (e.g. 0.05 = 5%)")
    args = parser.parse_args()

    tickers = ["AAPL", "MSFT", "GOOG", "META", "NVDA", "AMD", "INTC", "QCOM", "TSLA"]
    df = download_prices(tickers)

    # ✅ Ensure datetime index
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    print("Sample Prices:\n", df.head())

    if df.empty:
        print("Price data download failed. Please check ticker list or internet connection.")
        exit()

    coint_pairs = find_cointegrated_pairs(df, significance=0.1)
    print("\nCointegrated Pairs:")
    for pair in coint_pairs:
        print(pair)

    if not coint_pairs:
        print("\nNo cointegrated pairs found. Try adjusting threshold or ticker set.")
        exit()

    A, B, _ = coint_pairs[0]
    series_A = df[A]
    series_B = df[B]

    spread, beta = compute_spread(series_A, series_B)
    signals = generate_signals(spread)

    results = backtest_pair(
        series_A, series_B, signals, beta,
        capital_base=args.capital,
        risk_aversion=args.risk,
        slippage_pct=args.slippage,
        transaction_cost_pct=args.txn_cost,
        max_leverage=args.max_leverage,
        stop_loss_pct=args.stop_loss
    )

    # ✅ Confirm index type for proper CAGR logic
    if not isinstance(results.index, pd.DatetimeIndex):
        print("\n[Warning] Result index is not datetime. Setting it from price series...")
        results.index = series_A.index[1:]  # Align with price series (skip 1 for diff)

    print("\nBacktest Results (Last 5 Rows):\n", results.tail())

    trade_events = results[results["Event"].notna()]
    print(f"\nTrade Events Summary (First 5 rows):\n{trade_events.head()}")

    results["Capital"].plot(title=f"Capital Trajectory: {A} vs {B}", figsize=(10, 5))
    plt.xlabel("Date")
    plt.ylabel("Capital")
    plt.grid(True)
    plt.tight_layout()

    metrics = compute_metrics(results)
    print("\nPerformance Metrics:")
    for k, v in metrics.items():
        print(f"{k}: {v}")

    plt.show()

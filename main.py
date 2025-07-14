import argparse
from src.loader import download_prices
from src.coint import find_cointegrated_pairs
from src.strategy import compute_spread, generate_signals
from src.backtest import backtest_pair, compute_metrics
import matplotlib.pyplot as plt

if __name__ == "__main__":
    # CLI: Parse custom parameters
    parser = argparse.ArgumentParser(description="Statistical Arbitrage Backtest Runner")
    parser.add_argument("--capital", type=float, default=1_000_000, help="Initial capital base")
    parser.add_argument("--risk", type=float, default=1.0, help="Risk aversion parameter (higher = lower exposure)")
    parser.add_argument("--slippage", type=float, default=0.0005, help="Slippage cost as decimal (e.g., 0.001 = 10bps)")
    parser.add_argument("--txn_cost", type=float, default=0.001, help="Transaction cost as decimal (e.g., 0.001 = 10bps)")
    args = parser.parse_args()

    # 1. Download historical price data
    tickers = ["AAPL", "MSFT", "GOOG", "META", "NVDA", "AMD", "INTC", "QCOM", "TSLA"]
    df = download_prices(tickers)
    print("Sample Prices:\n", df.head())

    # Handle failed data fetches gracefully
    if df.empty:
        print("Price data download failed. Please check ticker list or internet connection.")
        exit()

    # 2. Find cointegrated pairs
    coint_pairs = find_cointegrated_pairs(df, significance=0.1)
    print("\nCointegrated Pairs:")
    for pair in coint_pairs:
        print(pair)

    if not coint_pairs:
        print("\nNo cointegrated pairs found. Try adjusting threshold or ticker set.")
        exit()

    # 3. Select top cointegrated pair
    A, B, _ = coint_pairs[0]
    series_A = df[A]
    series_B = df[B]

    # 4. Compute spread and generate signals
    spread, beta = compute_spread(series_A, series_B)
    signals = generate_signals(spread)

    # 5. Backtest strategy with user-defined parameters
    results = backtest_pair(
        series_A, series_B, signals, beta,
        capital_base=args.capital,
        risk_aversion=args.risk,
        slippage_pct=args.slippage,
        transaction_cost_pct=args.txn_cost
    )
    print("\nBacktest Results:\n", results.tail())

    # 6. Plot capital trajectory
    results["Capital"].plot(title=f"Capital Trajectory: {A} vs {B}", figsize=(10, 5))
    plt.xlabel("Date")
    plt.ylabel("Capital")
    plt.grid(True)
    plt.tight_layout()

    # 7. Compute and display key performance metrics
    metrics = compute_metrics(results)
    print("\nPerformance Metrics:")
    for k, v in metrics.items():
        print(f"{k}: {v}")

    plt.show()

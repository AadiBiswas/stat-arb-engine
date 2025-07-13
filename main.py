from src.loader import download_prices
from src.coint import find_cointegrated_pairs
from src.strategy import compute_spread, generate_signals
from src.backtest import backtest_pair, compute_metrics
import matplotlib.pyplot as plt

if __name__ == "__main__":
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

    # 5. Backtest strategy with capital-aware logic
    results = backtest_pair(series_A, series_B, signals, beta)
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

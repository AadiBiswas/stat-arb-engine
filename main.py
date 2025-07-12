from src.loader import download_prices
from src.coint import find_cointegrated_pairs
from src.strategy import compute_spread, generate_signals
from src.backtest import backtest_pair
import matplotlib.pyplot as plt

if __name__ == "__main__":
    # 1. Download historical price data
    tickers = ["AAPL", "MSFT", "GOOG", "META", "NVDA", "AMD", "INTC", "QCOM", "TSLA"]
    df = download_prices(tickers)
    print("Sample Prices:\n", df.head())

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

    # 5. Backtest strategy
    results = backtest_pair(series_A, series_B, signals, beta)
    print("\nBacktest Results:\n", results.tail())

    # 6. Plot cumulative PnL
    results["CumulativePnL"].plot(title=f"Cumulative PnL: {A} vs {B}", figsize=(10, 5))
    plt.xlabel("Date")
    plt.ylabel("PnL")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

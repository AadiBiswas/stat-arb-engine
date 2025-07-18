import argparse
import pandas as pd
import os
import matplotlib.pyplot as plt

from src.loader import download_prices
from src.coint import find_cointegrated_pairs
from src.strategy import compute_spread, generate_signals
from src.backtest import backtest_pair, compute_metrics
from src.config import load_config
from src.export import save_trade_log, save_full_results, save_summary_table
from src.features import extract_features
from ml.supervised_model import predict_success  # <- ML model prediction

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Statistical Arbitrage Backtest Runner")
    parser.add_argument("--config", type=str, default="config.json", help="Path to experiment config JSON")
    args = parser.parse_args()

    # Load config from JSON
    config = load_config(args.config)

    tickers = config.get("tickers", [])
    top_n = config.get("top_n", 3)
    df = download_prices(tickers)

    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    if df.empty:
        print("Price data download failed. Please check ticker list or internet connection.")
        exit()

    # Step 1: Find cointegrated pairs
    coint_pairs = find_cointegrated_pairs(df, significance=config.get("significance", 0.1))
    print("\nCointegrated Pairs:")
    for pair in coint_pairs:
        print(pair)

    if not coint_pairs:
        print("\nNo cointegrated pairs found. Try adjusting threshold or ticker set.")
        exit()

    results_list = []
    summary_rows = []
    feature_rows = []

    for A, B, pval in coint_pairs:
        try:
            series_A = df[A]
            series_B = df[B]
            spread, beta = compute_spread(series_A, series_B)
            signals = generate_signals(spread)

            results = backtest_pair(
                series_A, series_B, signals, beta,
                capital_base=config.get("capital", 1_000_000),
                risk_aversion=config.get("risk_aversion", 1.0),
                slippage_pct=config.get("slippage", 0.0005),
                transaction_cost_pct=config.get("txn_cost", 0.001),
                max_leverage=config.get("max_leverage", 2.0),
                stop_loss_pct=config.get("stop_loss", None)
            )

            if not isinstance(results.index, pd.DatetimeIndex):
                results.index = series_A.index[1:]

            metrics = compute_metrics(results)
            metrics.update({
                "Pair": f"{A}/{B}",
                "Beta": round(beta, 4),
                "P-Value": round(pval, 4)
            })

            features = extract_features(series_A, series_B, spread, signals, beta, pval)
            features["Pair"] = f"{A}/{B}"

            summary_rows.append(metrics)
            feature_rows.append(features)
            results_list.append((f"{A}_{B}", results))

            save_trade_log(results, f"{A}_{B}")
            save_full_results(results, f"{A}_{B}")

        except Exception as e:
            print(f"[Error] Backtest failed for pair {A}/{B}: {e}")

    if not summary_rows:
        print("No backtests succeeded.")
        exit()

    # Construct results table
    summary_df = pd.DataFrame(summary_rows)
    feature_df = pd.DataFrame(feature_rows)

    # Predict ML success probability for each strategy
    success_probas = predict_success(feature_df)
    summary_df["ML_Predicted_Success_Prob"] = success_probas

    # Sort using ML and Sharpe
    summary_df.sort_values(by=["ML_Predicted_Success_Prob", "Sharpe Ratio"], ascending=False, inplace=True)
    top_df = summary_df.head(top_n)

    print("\nTop Strategies:")
    print(top_df[["Pair", "Sharpe Ratio", "ML_Predicted_Success_Prob", "CAGR (%)", "Max Drawdown", "Total Return (%)"]])

    top_pair = top_df.iloc[0]["Pair"]
    for name, res in results_list:
        if name.replace("/", "_") == top_pair.replace("/", "_"):
            res["Capital"].plot(title=f"Top Strategy Capital Trajectory: {top_pair}", figsize=(10, 5))
            plt.xlabel("Date")
            plt.ylabel("Capital")
            plt.grid(True)
            plt.tight_layout()
            break

    # Save outputs
    os.makedirs("results", exist_ok=True)
    save_summary_table(summary_df, fmt="csv")
    save_summary_table(summary_df, fmt="html")
    feature_df.to_csv("results/features.csv", index=False)
    print("\n[Saved] Strategy features exported to 'results/features.csv'")

    plt.show()

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

from src.loader import download_prices
from src.config import load_config
from src.export import save_summary_table
from ml.supervised_model import predict_success
from ml.clustering import cluster_features
from src.coint import find_cointegrated_pairs
from src.strategy import compute_spread, generate_signals
from src.backtest import backtest_pair, compute_metrics
from src.features import extract_features

st.set_page_config(page_title="Stat-Arb Dashboard", layout="wide")

st.title("📈 Statistical Arbitrage Strategy Explorer")

# Sidebar config
config_path = st.sidebar.text_input("Config Path", value="config.json")
reload_btn = st.sidebar.button("Run Pipeline")

# Load config
if not os.path.exists(config_path):
    st.error("Config file not found!")
    st.stop()

config = load_config(config_path)
tickers = config["tickers"]
top_n = config["top_n"]

if reload_btn:
    st.info("Running full pipeline...")
    df = download_prices(tickers)

    # Run cointegration
    coint_pairs = find_cointegrated_pairs(df, significance=config.get("significance", 0.1))
    st.success(f"{len(coint_pairs)} cointegrated pairs found.")

    summary_rows = []
    feature_rows = []
    all_results = {}

    for A, B, pval in coint_pairs:
        try:
            sA = df[A]
            sB = df[B]
            spread, beta = compute_spread(sA, sB)
            signals = generate_signals(spread)

            results = backtest_pair(
                sA, sB, signals, beta,
                capital_base=config["capital"],
                risk_aversion=config["risk_aversion"],
                slippage_pct=config["slippage"],
                transaction_cost_pct=config["txn_cost"],
                max_leverage=config["max_leverage"],
                stop_loss_pct=config["stop_loss"]
            )

            metrics = compute_metrics(results)
            metrics.update({"Pair": f"{A}/{B}", "Beta": beta, "P-Value": pval})
            summary_rows.append(metrics)

            features = extract_features(sA, sB, spread, signals, beta, pval)
            features["Pair"] = f"{A}/{B}"
            feature_rows.append(features)

            all_results[f"{A}/{B}"] = results

        except Exception as e:
            st.warning(f"Error on {A}/{B}: {e}")

    summary_df = pd.DataFrame(summary_rows)
    feature_df = pd.DataFrame(feature_rows)

    # Save to disk
    os.makedirs("results", exist_ok=True)
    summary_df.to_csv("results/strategy_summary.csv", index=False)
    feature_df.to_csv("results/features.csv", index=False)

    # Clustering + ML
    clustered_df = cluster_features(n_clusters=config["regime_count"], plot=False)
    feature_df["Regime"] = clustered_df["Regime"]
    success_probas = predict_success(feature_df)
    summary_df["ML_Predicted_Success_Prob"] = success_probas

    # Filtering + sorting
    if config["use_regime_filtering"]:
        summary_df = summary_df[summary_df["Pair"].isin(feature_df["Pair"])]
        feature_df = feature_df[feature_df["Regime"].isin(config["regime_include"])]

    summary_df.sort_values(by=["ML_Predicted_Success_Prob", "Sharpe Ratio"], ascending=False, inplace=True)
    summary_df.to_csv("results/strategy_summary.csv", index=False)
    save_summary_table(summary_df, fmt="html")

    st.success("Pipeline complete!")

# Load final output
if os.path.exists("results/strategy_summary.csv"):
    final_df = pd.read_csv("results/strategy_summary.csv")
    st.subheader("🔝 Top Strategies")
    st.dataframe(final_df.head(top_n), use_container_width=True)

    # Plot top strategy
    top_pair = final_df.iloc[0]["Pair"]
    res_path = f"results/full_results/{top_pair.replace('/', '_')}.csv"
    if os.path.exists(res_path):
        capital_df = pd.read_csv(res_path, index_col=0, parse_dates=True)
        st.subheader(f"📊 Capital Trajectory: {top_pair}")
        st.line_chart(capital_df["Capital"])

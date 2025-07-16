import os
import pandas as pd

def save_trade_log(results: pd.DataFrame, pair_name: str, output_dir="logs"):
    """
    Save only the rows with trade events to a CSV file.

    Args:
        results (pd.DataFrame): Full backtest result with Event column
        pair_name (str): Symbolic name for the pair, e.g. "AAPL-MSFT"
        output_dir (str): Directory to save the file
    """
    os.makedirs(output_dir, exist_ok=True)
    trade_log = results[results["Event"].notna()]
    path = os.path.join(output_dir, f"{pair_name}_trades.csv")
    trade_log.to_csv(path)
    print(f"[Export] Trade log saved to {path}")


def save_full_results(results: pd.DataFrame, pair_name: str, output_dir="results"):
    """
    Save the entire results DataFrame to a CSV file.

    Args:
        results (pd.DataFrame): Full backtest results
        pair_name (str): Symbolic name for the pair, e.g. "AAPL-MSFT"
        output_dir (str): Directory to save the file
    """
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"{pair_name}_results.csv")
    results.to_csv(path)
    print(f"[Export] Full results saved to {path}")


def save_summary_table(summary: pd.DataFrame, output_dir="results", fmt="csv"):
    """
    Save strategy summary table (CAGR, Sharpe, etc.) to disk.

    Args:
        summary (pd.DataFrame): Strategy ranking table
        output_dir (str): Output directory
        fmt (str): 'csv' or 'html'
    """
    os.makedirs(output_dir, exist_ok=True)
    fname = f"strategy_summary.{fmt}"
    path = os.path.join(output_dir, fname)

    if fmt == "csv":
        summary.to_csv(path, index=False)
    elif fmt == "html":
        summary.to_html(path, index=False)
    else:
        raise ValueError("Unsupported format. Use 'csv' or 'html'.")

    print(f"[Export] Strategy summary saved to {path}")

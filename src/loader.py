import yfinance as yf
import pandas as pd
import os
import time

def download_prices(tickers, start="2015-01-01", end="2024-01-01", save=True):
    """
    Download adjusted close prices for a list of tickers.
    
    Retries once for failed tickers. Removes unrecoverable failures from final output.

    Args:
        tickers (list): List of stock tickers (e.g., ['AAPL', 'MSFT'])
        start (str): Start date in 'YYYY-MM-DD'
        end (str): End date in 'YYYY-MM-DD'
        save (bool): Whether to save the CSV to /data/raw/

    Returns:
        pd.DataFrame: Adjusted close prices with tickers as columns
    """
    print("Downloading price data...")
    df = pd.DataFrame()
    failed = []

    for ticker in tickers:
        try:
            temp = yf.download(ticker, start=start, end=end, auto_adjust=False)["Adj Close"]
            if temp.empty:
                raise ValueError("Empty data")
            df[ticker] = temp
        except Exception as e:
            print(f"[Warning] Initial download failed for {ticker}: {e}. Retrying...")
            time.sleep(1)
            try:
                temp = yf.download(ticker, start=start, end=end, auto_adjust=False)["Adj Close"]
                if temp.empty:
                    raise ValueError("Empty data on retry")
                df[ticker] = temp
            except Exception as e:
                print(f"[Error] Final download failed for {ticker}: {e}")
                failed.append(ticker)

    if failed:
        print(f"\nSkipped {len(failed)} tickers due to persistent errors: {failed}")

    df.dropna(axis=0, how="any", inplace=True)

    if save:
        os.makedirs("data/raw", exist_ok=True)
        df.to_csv("data/raw/prices.csv")

    return df

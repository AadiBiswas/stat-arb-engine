import yfinance as yf
import pandas as pd
import os

def download_prices(tickers, start="2015-01-01", end="2024-01-01", save=True):
    """
    Download adjusted close prices for a list of tickers.
    
    Args:
        tickers (list): List of stock tickers (e.g., ['AAPL', 'MSFT'])
        start (str): Start date in 'YYYY-MM-DD'
        end (str): End date in 'YYYY-MM-DD'
        save (bool): Whether to save the CSV to /data/raw/

    Returns:
        pd.DataFrame: Adjusted close prices with tickers as columns
    """
    df = yf.download(tickers, start=start, end=end, auto_adjust=False)["Adj Close"]
    
    # Ensure DataFrame format (in case only one ticker is passed)
    if isinstance(df, pd.Series):
        df = df.to_frame(name=tickers[0])
    
    df.dropna(axis=0, how="any", inplace=True)
    
    if save:
        os.makedirs("data/raw", exist_ok=True)
        df.to_csv("data/raw/prices.csv")

    return df

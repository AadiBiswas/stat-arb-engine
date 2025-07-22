# src/alpaca_loader.py

import os
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, StockLatestTradeRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta
import pandas as pd

# Load environment variables
load_dotenv()

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
    raise EnvironmentError("Missing Alpaca API credentials in .env file")

# Initialize client
client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)

def fetch_historical_data(symbol: str, days: int = 5, timeframe: str = "day") -> pd.DataFrame:
    """
    Fetch historical bars for a given stock symbol from Alpaca.

    Args:
        symbol (str): Ticker (e.g., 'AAPL')
        days (int): Number of days to look back
        timeframe (str): One of 'minute', 'hour', 'day'

    Returns:
        pd.DataFrame: Historical OHLCV data
    """
    now = datetime.utcnow()
    start = now - timedelta(days=days)

    tf_map = {
        "minute": TimeFrame.Minute,
        "hour": TimeFrame.Hour,
        "day": TimeFrame.Day
    }

    if timeframe not in tf_map:
        raise ValueError("Invalid timeframe. Choose from 'minute', 'hour', or 'day'.")

    request_params = StockBarsRequest(
        symbol_or_symbols=[symbol],
        timeframe=tf_map[timeframe],
        start=start,
        end=now
    )

    try:
        bars = client.get_stock_bars(request_params).df
        df = bars.loc[symbol].reset_index()
        df.rename(columns={"timestamp": "datetime"}, inplace=True)
        return df
    except Exception as e:
        print(f"[Error] Failed to fetch data for {symbol}: {e}")
        return pd.DataFrame()

def fetch_latest_trade(symbol: str):
    """
    Fetch the most recent trade for a given stock.

    Args:
        symbol (str): Ticker symbol

    Returns:
        dict or None
    """
    try:
        request = StockLatestTradeRequest(symbol_or_symbols=[symbol])
        trade = client.get_stock_latest_trade(request)
        return trade[symbol].__dict__
    except Exception as e:
        print(f"[Error] Failed to fetch latest trade for {symbol}: {e}")
        return None

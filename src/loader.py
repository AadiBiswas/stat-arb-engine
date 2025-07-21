import os
import time
import pandas as pd
import yfinance as yf
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    import alpaca_trade_api as tradeapi
except ImportError:
    tradeapi = None  # Alpaca support optional

def download_prices(tickers, start="2015-01-01", end="2024-01-01", save=True, mode="historical"):
    """
    Download adjusted close prices for a list of tickers.

    Args:
        tickers (list): List of stock tickers (e.g., ['AAPL', 'MSFT'])
        start (str): Start date (only used in historical mode)
        end (str): End date (only used in historical mode)
        save (bool): Save to CSV under data/raw/
        mode (str): 'historical' (Yahoo) or 'live' (Alpaca)

    Returns:
        pd.DataFrame: Adjusted close prices
    """
    df = pd.DataFrame()
    failed = []

    if mode == "live":
        print("🔄 Attempting to load LIVE prices from Alpaca...")

        if tradeapi is None:
            print("[Error] alpaca-trade-api not installed. Falling back to Yahoo.")
            mode = "historical"
        else:
            api_key = os.getenv("ALPACA_API_KEY")
            api_secret = os.getenv("ALPACA_SECRET_KEY")
            base_url = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

            if not api_key or not api_secret:
                print("[Warning] Missing Alpaca credentials in .env. Falling back to Yahoo.")
                mode = "historical"
            else:
                try:
                    alpaca = tradeapi.REST(api_key, api_secret, base_url)
                    now = datetime.utcnow().isoformat()
                    for ticker in tickers:
                        try:
                            barset = alpaca.get_bars(ticker, "1Min", limit=1).df
                            if barset.empty:
                                raise ValueError("Empty barset")
                            last_price = barset["close"].iloc[-1]
                            df.loc[pd.Timestamp.now(), ticker] = last_price
                        except Exception as e:
                            print(f"[Error] Failed live fetch for {ticker}: {e}")
                            failed.append(ticker)
                except Exception as e:
                    print(f"[Error] Alpaca API failure: {e}")
                    mode = "historical"

    if mode == "historical":
        print("📚 Downloading HISTORICAL prices from Yahoo Finance...")
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
        print(f"\n⚠️ Skipped {len(failed)} tickers due to errors: {failed}")

    df.dropna(axis=0, how="any", inplace=True)

    if save:
        os.makedirs("data/raw", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") if mode == "live" else ""
        suffix = f"_live_{timestamp}" if mode == "live" else ""
        df.to_csv(f"data/raw/prices{suffix}.csv")
        print(f"[Saved] Price data to 'data/raw/prices{suffix}.csv'")

    return df

if __name__ == "__main__":
    tickers = ["AAPL", "MSFT", "GOOG"]
    df = download_prices(tickers, mode="live", save=False)
    print(df.tail())

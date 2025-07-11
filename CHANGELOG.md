# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2025-07-11

### Added
- **Price Loader (`loader.py`)**: Introduced core data ingestion module using `yfinance`.
  - Downloads historical adjusted close prices for any list of tickers.
  - Handles missing values and formats output as a clean Pandas DataFrame.
  - Saves raw price data to `data/raw/prices.csv` for persistence and reproducibility.

### Notes
- First commit in the Statistical Arbitrage Engine project.
- Focused on modular design and reusability for downstream processing.

### Next
- **main.py**: Create centralized CLI to run full pipeline and plot cumulative PnL.
- **coint.py**: Identify cointegrated pairs via Engle-Granger test and return ranked results.
- **strategy.py**: Construct spreads using OLS hedge ratios; generate z-score-based entry/exit signals.
- **backtest.py**: Track positions, PnL, and cumulative returns for a single pair over historical data.

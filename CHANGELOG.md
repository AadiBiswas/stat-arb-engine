# Changelog

All notable changes to this project will be documented in this file.


## [0.2.0] - 2025-07-12

### Added
- **main.py**: Centralized runner to execute full stat-arb pipeline:
  - Loads historical price data
  - Identifies cointegrated pairs
  - Constructs spreads and signals for top pair
  - Backtests cumulative PnL and plots result

- **Cointegration Module (`coint.py`)**: Implements Engle-Granger cointegration test across all pairwise combinations.
  - Returns all pairs with p-value below user-defined threshold.
  - Sorts pairs by strength of cointegration (lowest p-value first).

- **Spread Strategy Module (`strategy.py`)**: 
  - Estimates hedge ratio via OLS regression.
  - Constructs spread and computes z-score-based entry/exit signals.
  - Signals are cleanly aligned with price data to avoid mismatched index errors.

- **Backtest Engine (`backtest.py`)**:
  - Simulates PnL for long/short positions based on signal direction.
  - Tracks and returns cumulative returns over the full trading period.
  - Fully modular, plug-and-play with any valid pair and signal set.

### Notes
- First end-to-end simulation successfully completed on a live pair (e.g., `AMD`/`MSFT`).
- Cumulative PnL correctly reflects entry and exit signals; visual output confirms trade activity over time.
- Clean separation of concerns across modules — designed for extensibility into metrics, execution models, and multi-pair batch runs.

### Next
- **backtest.py**: Add Sharpe Ratio, Max Drawdown, Win %, Trade Count, and CAGR metrics.
- **strategy.py**: Support dynamic position sizing and volatility-aware thresholding.
- **main.py**: Add CLI or config-driven controls for entry/exit z-scores, capital size, and backtest options.
- Begin building a **multi-pair backtest framework** for strategy comparison and ranking.


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

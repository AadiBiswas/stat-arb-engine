# Changelog

All notable changes to this project will be documented in this file.

## [0.5.0] - 2025-07-15

### Enhanced

- **backtest.py**:
  - Added **long/short exposure limits** via `max_leverage` cap.
  - Implemented **event tagging**: each trade is labeled as "Entry", "Exit", or "StopLoss".
  - Integrated **stop-loss logic**, triggered if PnL falls below a capital-relative threshold.
  - Exposure logic now includes directional sizing with risk-adjusted scaling and tagged triggers.
  - Appends **event column** to backtest result, improving traceability of strategy behavior.

- **main.py**:
  - CLI now supports:
    - `--capital`: Starting capital for simulation
    - `--risk`: Risk aversion factor (higher = smaller positions)
    - `--slippage`: Execution slippage per trade
    - `--txn_cost`: Transaction cost per trade
    - `--max_leverage`: Limit on position exposure
    - `--stop_loss`: Optional stop-loss threshold
  - Prints a **trade event summary** including entries, exits, and stops.
  - CLI-based config enables easy experimentation with strategy parameters.

### Notes

- All core mechanics of **Phase 2** have now been implemented:
  - ✅ Capital tracking and leverage limits
  - ✅ Transaction cost and slippage modeling
  - ✅ Performance metrics including Sharpe, Drawdown, Win Ratio, Trade Count
  - ✅ New: Exposure limits, Stop-loss logic, Event tagging

- The engine can now simulate realistic capital usage with traceable, event-driven trade annotations — a prerequisite for robust statistical arbitrage evaluation.

### Next

We now enter **Phase 3**, which will include:

- **Batch Simulation**: Run all cointegrated pairs in parallel
-  **Strategy Ranking**: Score based on Sharpe, CAGR, Drawdown, etc.
- **Config-Driven Runs**: Optional YAML/JSON config or CLI flags to control:
  - Lookback window
  - Z-score thresholds
  - Position sizing logic
- **Result Export**: Save ranked result table as CSV and/or styled HTML for analysis and presentation


## [0.4.0] - 2025-07-14

### Enhanced
- **backtest.py**:
  - Added **slippage** and **transaction cost modeling** to simulate execution-aware PnL.
  - Incorporated **capital base**, **risk aversion**, and **dynamic position sizing**.
  - Exposure now reflects leverage-adjusted directional positions; max leverage capped at 2× by default.

- **main.py**:
  - Introduced **CLI support** using `argparse`; allows user to control:
    - `--capital` (starting capital),
    - `--slippage` (bps per unit),
    - `--txn_cost` (per-trade cost),
    - `--risk_aversion` (position scaling),
    - `--tickers` (custom list override).
  - Gracefully handles empty dataframes or failed ticker fetches.
  - Capital trajectory is now plotted instead of naive cumulative PnL.

### Notes
- This release simulates a **realistic execution model** — incorporating both trading frictions and capital constraints.
- Position size scales dynamically with spread z-score, bounded by volatility and user risk aversion.
- CLI interface enables batch testing and fine-grained control, supporting future experiment logging and automation.
- Slippage and costs are parameterized and easy to extend for future improvements.

### Next
- **Exposure Constraints**: Add upper/lower bounds on long/short position exposure.
- **Event Tagging**: Record entry/exit/stop-loss timestamps and triggers in results.
- **Trade Logger**: Save detailed trade ledger (entry/exit prices, timestamps, size) for traceability.
- **Multi-Pair Backtesting**: Generalize to evaluate and rank top N cointegrated pairs.


## [0.3.0] - 2025-07-13

### Enhanced
- **backtest.py**: Overhauled backtest logic with full capital and exposure tracking.
  - Introduced dynamic position sizing proportional to signal strength.
  - Added capital-aware PnL calculation and cumulative growth.
  - Output includes spread, z-score, signal, position size, exposure, PnL, and capital trajectory.

- **main.py**: Updated execution script to:
  - Plot **capital** trajectory instead of raw cumulative PnL.
  - Compute and display **Sharpe Ratio**, **Max Drawdown**, **Win Ratio**, and **Trade Count**.
  - Handles data gaps more gracefully; cleaner pipeline from data to metrics.

- **loader.py**: Hardened price download routine.
  - Retries failed tickers up to 3 times.
  - Excludes unrecoverable tickers from the final dataframe instead of failing the pipeline.
  - Ensures pipeline resilience during partial or unstable data fetches.

### Notes
- Pipeline now returns a **fully capital-aware trading simulation**, setting up the foundation for execution modeling (slippage, txn costs, leverage).
- `main.py` executes cleanly even if some tickers fail to download — fallback mechanisms and index alignment are now robust.
- Visual output now better represents **actual strategy growth** under realistic constraints (capital-based scaling and reinvestment).

### Next
- **Execution modeling**: Add per-trade slippage and transaction costs into backtest engine.
- **Exposure constraints**: Introduce leverage cap, position limits, and optional stop-loss logic.
- **Multi-pair support**: Generalize engine to backtest and compare top cointegrated pairs in batch mode.
- **Event tagging**: Annotate entry, exit, and stop-loss points in time-series for trade traceability.


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

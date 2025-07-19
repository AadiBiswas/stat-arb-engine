# Changelog

All notable changes to this project will be documented in this file.

## [0.7.2] - 2025-07-19

### Added
- **clustering.py**:
  - New unsupervised learning module using `KMeans` for regime detection.
  - Applies clustering to strategy feature vectors and assigns regime labels.
  - Optionally visualizes cluster structure using PCA.
  - Saves updated feature set with regime column to `results/features.csv`.

### Enhanced
- **features.py**:
  - Added support for regime integration: cluster assignments now tracked per pair.
  - Modular design supports supervised and unsupervised feature workflows.

- **main.py**:
  - Integrated regime filtering and ML label threshold from `config.json`.
  - Now filters final strategies by cluster assignment (`regime_include`) and restricts selection accordingly.
  - Embeds KMeans clustering step automatically in the backtest pipeline if enabled.

- **supervised_model.py**:
  - Generalized label logic with config-driven `"ml_label_metric"` and `"ml_label_threshold"`.
  - Enables flexible definitions of "success" for predictive modeling (e.g., Sharpe > 1, CAGR > 10%, etc.).

- **config.json**:
  - New keys:
    - `use_regime_filtering`: whether to apply regime filters to results.
    - `regime_count`: number of KMeans clusters.
    - `regime_include`: list of regime IDs to keep.
    - `ml_label_metric`: which metric to use for labeling success.
    - `ml_label_threshold`: threshold to classify strategy as "successful".

### Notes
- This release completes **Phase 4.2–4.3**:
  - The engine now supports **regime-aware predictive modeling**, opening the door for time-varying strategy gating, clustering-based portfolio filtering, and alpha decomposition across unsupervised regimes.
  - Clustering is designed to be optional and tunable via config.

- The system supports dual pipelines:
  - **Supervised** (Random Forest, etc.) to predict success probability.
  - **Unsupervised** (KMeans) to identify and rank regime clusters.

### Next
- **Phase 4.4: Intelligent Filtering and Strategy Activation**
  - Add optional strategy filters based on:
    - ML-predicted success probability threshold.
    - Regime-specific exclusions.
  - Begin integrating regime-tracking in strategy ledger for regime rotation studies.
  - Add support for GMM or spectral clustering in `clustering.py` for non-linear regime boundaries.


## [0.7.1] - 2025-07-18

### Added
- **requirements.txt**:
  - Added `scikit-learn`, `joblib`, `matplotlib`, and `pandas` to support supervised learning.
  - Enables model training, evaluation, and integration into the main stat-arb pipeline.

### Enhanced
- **main.py**:
  - Integrated trained classifier (`models/rf_model.pkl`) into execution pipeline:
    - Loads model if available.
    - Computes success probability (`P(Success)`) for each pair and appends it to summary output.
    - Handles missing model gracefully without halting pipeline.
  - Summary output (`strategy_summary.csv` and `.html`) now includes ML prediction.

- **supervised_model.py**:
  - Enhanced to support **inference mode**:
    - Loads features and labels from disk.
    - Applies pre-trained model to compute classification accuracy and predict success.
    - Prints full classification report and confusion matrix.

### Notes
- This completes **Phase 4.2: Supervised Prediction Layer**.
- The pipeline now supports end-to-end **meta-quant feedback**:
  - Extracts features → trains classifier → scores strategies.
- Probabilities can now be used for **strategy gating**, **weighting**, or **ranking enhancements**.

### Next
- **Phase 4.3–4.4: Regime Detection + Strategy Switching**
  - Integrate clustering (e.g., KMeans, GMM) for unsupervised regime segmentation.
  - Add regime classifiers to determine when specific pairs or strategy types should be active/inactive.
  - Optional config flag to toggle supervised prediction, filtering, or model retraining from CLI.
  - Later extension: XGBoost classifier and hyperparameter optimization for higher prediction accuracy.


## [0.7.0] - 2025-07-17

### Added
- **features.py**:
  - New feature engineering module for ML-based strategy modeling.
  - Extracts per-pair metrics including:
    - Spread volatility and mean-reversion strength
    - Signal statistics (mean, std, zero-crossing rate)
    - Hedge ratio (beta), ADF statistic, and p-value
  - Enables integration with supervised/unsupervised models in future phases.

- **supervised_model.py**:
  - Scaffold for machine learning classifier to predict strategy success.
  - Prepares integration for XGBoost, Random Forest, or other model types.
  - Designed to consume `results/features.csv` and return probabilities or regime predictions.

### Enhanced
- **main.py**:
  - Embedded feature extraction directly into cointegrated-pair backtesting loop.
  - For each pair, in addition to summary metrics:
    - Extracts model-ready features
    - Stores all features in `results/features.csv` for training/testing ML models.
  - All outputs remain consistent:
    - `strategy_summary.csv` + `.html` (metrics)
    - `features.csv` (ML)
    - `trade_logs/`, `full_results/` (granular records)

### Notes
- This marks the completion of **Phase 4.1**:
  - Transforming historical simulation into a **meta-learning pipeline**.
  - The engine now supports research into **predictive regime classification**, **alpha filtering**, and strategy gating using features.

### Next
- **Phase 4.2–4.4: Meta-Quant Intelligence**
  - Train supervised model to predict Sharpe ratio success or classify good/bad regimes.
  - Use model predictions to **filter, weight, or toggle** strategies in deployment.
  - Add CLI or config flag to activate `supervised_model.py` at runtime.
  - Future extension: Use unsupervised clustering (e.g., KMeans, GMM) for **regime detection** or **market structure labeling**.


## [0.6.0] - 2025-07-16

### Added
- **config.py**:
  - Introduced `load_config()` to ingest JSON-based experiment definitions.
  - Allows full override of CLI defaults; supports hybrid use.
  - Enables reproducible strategy experimentation via named config files.

- **export.py**:
  - Added CSV + HTML export module.
  - Saves strategy summary (Sharpe, CAGR, Drawdown, Win Ratio, etc.) for all backtested pairs.
  - Ensures results are human-readable and easy to share/analyze externally.

- **config.json**:
  - Sample config file added in root directory to define:
    - `tickers`, `capital`, `risk_aversion`, `slippage`, `txn_cost`,
    - `max_leverage`, `stop_loss`, `significance`, and `top_n`.

### Enhanced
- **main.py**:
  - Refactored for **batch backtesting** of all cointegrated pairs.
  - Displays top `N` strategies sorted by Sharpe Ratio.
  - Plots capital trajectory for best-performing pair.
  - Accepts both `--config config.json` and CLI-based argument overrides.
  - Saves strategy summary to `results/strategy_summary.csv` and `strategy_summary.html`.

### Notes
- This release completes **Phase 3**: moving from single-pair evaluation to **multi-pair experimentation** and reporting.
- Output can now be piped into spreadsheets or dashboards for quant research comparison.

### Next
- **Phase 4: Strategy Enhancements**
  - Execution modeling: simulate bid/ask fills, partial fills, queue slippage.
  - Regime switching: incorporate volatility clustering or macro signals.
  - Stop-loss/take-profit refinement: configurable triggers.
  - ML/optimizer-based parameter sweeps to tune thresholds (e.g., z-score entry).
  - Strategy ledger: track trades, entry/exit tags, and mark-to-market exposure across time.


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

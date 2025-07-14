# Statistical Arbitrage Engine

**Work in Progress 🚧**

## Overview  
This project implements a scalable, modular **statistical arbitrage engine** for cointegrated pairs. Designed for both **academic research** and **pre-production simulation**, it identifies trading opportunities across historical data and backtests mean-reversion strategies with full risk and return metrics.


## Goals
- Design modular framework for pair trading strategy simulation.
- Develop interpretable backtest metrics to compare pair performance.
- Extend toward ML-based pair scoring and live execution.
- Optimize for clarity, reproducibility, and extensibility.

## Pipeline Architecture  
- **Price Loader**: Downloads and preprocesses historical adjusted-close data.
- **Cointegration Scanner**: Applies Engle-Granger tests across all pair combinations.
- **Spread Constructor**: Uses OLS regression to estimate hedge ratio and build spreads.
- **Signal Generator**: Uses z-score thresholds to trigger long/short positions.
- **Backtester**: Calculates daily returns, cumulative PnL, and strategy diagnostics.

## Metrics (Planned and Ongoing)
- ✅ Cumulative Return  
- ✅ Trade Signals and PnL  
- ⏳ Sharpe Ratio  
- ⏳ Max Drawdown  
- ⏳ Win Ratio, Trade Count  
- ⏳ CAGR, Exposure Time  

## Execution Model (Planned)
- Capital base and leverage support  
- Position sizing based on volatility or risk budget  
- Slippage and transaction cost modeling  

## Extensions Under Consideration
- **Batch Pair Evaluation**: Test and rank dozens of pairs by strategy performance.
- **Strategy Config CLI**: User-defined thresholds, lookbacks, filters.
- **ML Meta-Models**: Predict regime shifts, pair success probability, or signal strength.
- **Live Execution Hooks**: Integration with Alpaca, Polygon, or Binance for real-time simulation.

## HOW TO RUN BACKTESTS FROM TERMINAL:

- **Step 1**: Activate your virtual environment  
  ```bash
  source venv/bin/activate

- **Step 2a**: Run the main engine with default parameters (no flags needed)
  ```bash
  python main.py

- **Step 2b**: Or, configure your own backtest with CLI arguments
  ```bash
  python main.py \
  --capital 1000000 \
  --slippage 0.0005 \
  --txn_cost 1.00 \
  --risk_aversion 1.0 \
  --tickers AAPL MSFT NVDA META

- **Arguments (Step 2b):**

    --`capital`: Initial capital base (e.g. `1_000_000`)

    --`slippage`: Per-unit slippage cost (e.g. `0.0005` for 5bps)

    --`txn_cost`: Flat transaction cost per trade (e.g. `$1.00`)

    --`risk_aversion`: Higher means smaller positions for same z-score

    --`tickers`: Override default ticker list with custom selection

## Sample Output

```
Cointegrated Pairs:
('AMD', 'MSFT', 0.0011)
('AAPL', 'AMD', 0.0193)

Backtest Results:
                Spread  ZSignal       PnL  CumulativePnL
Date                                                   
2023-12-27  -7.069978     -1.0  0.000000     132.777638
2023-12-28  -4.875373     -1.0 -2.194605     130.583033
2023-12-29  -6.536485     -1.0  1.661111     132.244145

```

## License  
MIT License.

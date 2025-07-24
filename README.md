# Statistical Arbitrage Engine

**Live-Ready · ML-Integrated · Modular Pipeline for Quantitative Pair Trading**

## Overview  
This project implements a **scalable, extensible statistical arbitrage engine** for identifying and simulating mean-reversion trading strategies using cointegrated asset pairs.

Designed for **quant research**, **ML experimentation**, and **pre-production simulation**, the system supports both **historical backtests** and **live data ingestion via Alpaca**. Features include full strategy diagnostics, regime-aware ML scoring, and interactive dashboard visualization.

---

## 🧠 Core Goals
- Simulate and compare statistical arbitrage strategies across pairs
- Build interpretable metrics: Sharpe, drawdown, success probability, etc.
- Predict strategy viability using supervised ML and clustering
- Integrate live data APIs (Alpaca) for real-time simulation or alerting
- Enable end-to-end workflows for **aspiring quants and ML researchers**

---

## 🧩 Pipeline Architecture  

- **Price Loader**: Supports `yfinance` (historical) and `Alpaca` (live) APIs
- **Cointegration Scanner**: Engle-Granger tests with adjustable significance
- **Spread & Signal Generator**: Z-score based entry/exit signal logic
- **Backtester**: Full capital accounting, PnL, slippage, leverage, stop loss
- **Feature Extractor**: Converts pair results into ML-ready feature vectors
- **ML Model**: RandomForest classifier for predicting success probabilities
- **Clustering**: Regime detection via KMeans on feature space
- **Streamlit Dashboard**: Interactive visualization of top pairs and capital curves

---

## 📈 Metrics Tracked
- ✅ Cumulative Return  
- ✅ Sharpe Ratio  
- ✅ Max Drawdown  
- ✅ CAGR, Win Rate, Exposure Time  
- ✅ Predicted Success Probability (ML)
- ✅ Regime Label (Unsupervised Clustering)

---

## ⚙️ Execution Model
- Configurable capital base and leverage
- Volatility-aware position sizing
- Slippage and flat transaction cost modeling
- Stop-loss logic to limit tail risk

---

## 🚀 How to Run the Engine

### Step 1: Install dependencies and setup virtual environment
```bash
pip install -r requirements.txt
```

---

### Step 2: Prepare environment variables

Create a `.env` file in your project root, or copy from `.env.example`:

```bash
cp .env.example .env
```

Then paste your [Alpaca API keys](https://alpaca.markets) into `.env`:

```env
# Alpaca API credentials
ALPACA_API_KEY=your_real_api_key_here
ALPACA_SECRET_KEY=your_real_secret_key_here
ALPACA_PAPER_URL=https://paper-api.alpaca.markets
ALPACA_DATA_URL=https://data.alpaca.markets
```

---

### Step 3: Run from terminal

#### Option A: Historical backtest (default)

```bash
python main.py
```

#### Option B: Live data ingestion via Alpaca

```bash
python main.py --data_source live
```

#### Option C: Full override with custom parameters

```bash
python main.py \
  --data_source live \
  --capital 1000000 \
  --slippage 0.0005 \
  --txn_cost 1.00 \
  --risk_aversion 1.0 \
  --tickers AAPL MSFT NVDA META
```

---

### Optional CLI Flags

| Flag              | Description                                               |
|------------------|-----------------------------------------------------------|
| `--data_source`   | `"historical"` (default) or `"live"`                      |
| `--capital`       | Initial capital base (e.g. `1000000`)                     |
| `--slippage`      | Per-unit slippage (e.g. `0.0005`)                          |
| `--txn_cost`      | Flat cost per trade (e.g. `1.00`)                          |
| `--risk_aversion` | Higher = smaller positions                                |
| `--tickers`       | Override ticker list with space-separated values          |

---

## 📊 Streamlit Dashboard (Interactive)

Launch a visual UI to explore strategy results:

```bash
streamlit run streamlit_app.py
```

- Upload or specify config
- Run full pipeline in-browser
- View ML-ranked top strategies
- Plot capital trajectory of best pair

---

## ✅ Testing and CI/CD

GitHub Actions automatically runs a CI workflow (`.github/workflows/ci.yml`) that:

- Validates default pipeline run
- Checks for ticker accessibility
- Flags Yahoo/Alpaca API issues
- Ensures all scripts compile without error

---

## 📁 File Structure Overview

```
├── main.py                 # Main entry point
├── streamlit_app.py        # Streamlit dashboard
├── .env                    # Local environment variables
├── .env.example            # Template for public sharing
├── config.json             # Strategy + model config
├── src/
│   ├── loader.py           # General price loader
│   ├── alpaca_loader.py    # Real-time ingestion (Alpaca)
│   ├── strategy.py         # Signals and position logic
│   ├── backtest.py         # Trade simulation and PnL
│   ├── coint.py            # Cointegration testing
│   └── export.py           # Save to disk
├── ml/
│   ├── clustering.py       # Unsupervised KMeans
│   ├── supervised_model.py # RandomForest predictor
│   └── utils.py            # Feature extraction
└── results/                # CSVs, models, plots
```

---

## 📦 Sample Output

```
Cointegrated Pairs:
('AAPL', 'NVDA', 0.0021)
('MSFT', 'META', 0.0045)

Backtest Summary:
    Pair        Sharpe    MaxDD    ML_P(Success)
    AAPL/NVDA   1.23      -7.8%     0.81
    MSFT/META   1.01      -5.4%     0.74
```

```

                Spread  ZSignal       PnL  CumulativePnL
Date                                                   
2023-12-27  -7.069978     -1.0  0.000000     132.777638
2023-12-28  -4.875373     -1.0 -2.194605     130.583033
2023-12-29  -6.536485     -1.0  1.661111     132.244145

```

---

## 🧠 Ideal For

- Aspiring **quant traders** and **ML researchers**
- Students exploring **mean-reversion, cointegration, or time series prediction**
- Engineers extending toward **live alerts, CI/CD, or strategy automation**
- Anyone interested in **market microstructure**, **regime modeling**, or **backtesting infra**

---

## 🪪 License

MIT License







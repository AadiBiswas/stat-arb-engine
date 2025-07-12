import pandas as pd
import numpy as np
import statsmodels.api as sm

def compute_spread(series1, series2):
    """
    Estimate hedge ratio via OLS and compute spread = series1 - beta * series2
    """
    # Preserve original index
    index = series1.index

    # Convert to NumPy arrays for regression
    y = series1.values
    X = sm.add_constant(series2.values)
    
    # Fit OLS model
    model = sm.OLS(y, X).fit()
    beta = model.params[1]

    # Compute spread and return as Series with original index
    spread = y - beta * series2.values
    return pd.Series(spread, index=index), beta


def generate_signals(spread, entry_z=1.0, exit_z=0.0):
    """
    Create long/short signals based on z-score of spread.
    
    Returns a Series of: 1 (long spread), -1 (short spread), or 0 (neutral)
    """
    zscore = (spread - np.mean(spread)) / np.std(spread)
    signals = np.zeros_like(zscore)

    # Entry conditions
    signals[zscore > entry_z] = -1  # Short spread
    signals[zscore < -entry_z] = 1  # Long spread

    # Exit condition
    signals[np.abs(zscore) < exit_z] = 0

    return pd.Series(signals, index=spread.index)

import numpy as np
import pandas as pd

def extract_features(series1, series2, spread, zscore, beta, pval):
    """
    Generate ML-ready features from spread and series pair.
    """
    volatility = spread.rolling(20).std().iloc[-1]
    mean_zscore = zscore.mean()
    std_zscore = zscore.std()
    max_zscore = zscore.max()
    min_zscore = zscore.min()
    z_crosses = ((zscore.shift(1) * zscore) < 0).sum()  # sign flips = mean crossings
    half_life = estimate_half_life(spread)

    return {
        "Volatility": round(volatility, 4),
        "MeanZ": round(mean_zscore, 4),
        "StdZ": round(std_zscore, 4),
        "MaxZ": round(max_zscore, 4),
        "MinZ": round(min_zscore, 4),
        "ZCrossings": int(z_crosses),
        "HalfLife": round(half_life, 2),
        "Beta": round(beta, 4),
        "P-Value": round(pval, 4),
    }

def estimate_half_life(spread):
    """
    Estimate mean-reversion half-life using OLS on lagged series.
    """
    spread = spread.dropna()
    if len(spread) < 2:
        return np.nan

    lagged = spread.shift(1).dropna()
    delta = (spread - lagged).dropna()

    if len(lagged) != len(delta):
        return np.nan

    beta = np.polyfit(lagged, delta, 1)[0]
    if beta >= 0:
        return np.nan

    halflife = -np.log(2) / beta if beta != 0 else np.nan
    return halflife

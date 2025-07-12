import pandas as pd
import itertools
from statsmodels.tsa.stattools import coint

def find_cointegrated_pairs(price_df, significance=0.2):
    """
    Test all pairs for cointegration and return those below the significance threshold.

    Args:
        price_df (pd.DataFrame): DataFrame of price series (one column per ticker)
        significance (float): p-value threshold for cointegration

    Returns:
        list of tuples: (ticker1, ticker2, p-value)
    """
    tickers = price_df.columns
    coint_pairs = []

    for pair in itertools.combinations(tickers, 2):
        series1 = price_df[pair[0]]
        series2 = price_df[pair[1]]
        _, pval, _ = coint(series1, series2)

        if pval < significance:
            coint_pairs.append((pair[0], pair[1], round(pval, 4)))

    coint_pairs.sort(key=lambda x: x[2])  # Sort by p-value ascending
    return coint_pairs

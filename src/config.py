import json
import os

def load_config(config_path, override_source=None):
    """
    Load experiment configuration from a JSON file.

    Returns:
        dict: Parameters such as tickers, thresholds, capital, cost assumptions, etc.
    """
    with open(config_path, "r") as f:
        config = json.load(f)

    if override_source:
        config["data_source"] = override_source

    return config



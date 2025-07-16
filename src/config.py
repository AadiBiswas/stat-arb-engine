import json
import os

def load_config(path="config.json"):
    """
    Load experiment configuration from a JSON file.

    Returns:
        dict: Parameters such as tickers, thresholds, capital, cost assumptions, etc.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"[Config Error] Config file not found at: {path}")

    with open(path, "r") as f:
        config = json.load(f)

    return config

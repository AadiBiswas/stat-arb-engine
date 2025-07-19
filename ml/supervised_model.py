import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

MODEL_PATH = "models/rf_model.pkl"

def load_data(feature_path="results/features.csv", label_path="results/strategy_summary.csv", label_metric="Sharpe Ratio", threshold=1.0):
    """
    Merge features and labels; binarize label into success/failure based on threshold.
    Keeps Regime as a feature.
    """
    features = pd.read_csv(feature_path)
    labels = pd.read_csv(label_path)

    merged = pd.merge(features, labels, on="Pair")
    merged["Success"] = (merged[label_metric] >= threshold).astype(int)

    drop_cols = ["Pair", "Success"]
    if label_metric in merged.columns:
        drop_cols.append(label_metric)

    X = merged.drop(columns=drop_cols, errors="ignore")
    y = merged["Success"]

    return X, y, merged

def train_random_forest(X, y, save_path=MODEL_PATH):
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    scores = cross_val_score(clf, X, y, cv=5)
    print(f"Cross-validated accuracy: {scores.mean():.4f}")

    clf.fit(X, y)
    joblib.dump(clf, save_path)
    print(f"[Saved] RandomForest model to {save_path}")
    return clf

def evaluate_model(clf, X, y):
    y_pred = clf.predict(X)
    print("\nConfusion Matrix:")
    print(confusion_matrix(y, y_pred))
    print("\nClassification Report:")
    print(classification_report(y, y_pred))

def predict_success(features_df, model_path=MODEL_PATH):
    """
    Predict probability of success from features (including Regime).
    """
    if not os.path.exists(model_path):
        print("[Warning] No trained model found. Skipping prediction.")
        return pd.Series([1.0] * len(features_df))  # optimistic default

    clf = joblib.load(model_path)

    drop_cols = ["Pair"]
    if "Success" in features_df.columns:
        drop_cols.append("Success")

    X = features_df.drop(columns=drop_cols, errors="ignore")
    probas = clf.predict_proba(X)[:, 1]
    return pd.Series(probas, index=features_df.index)

if __name__ == "__main__":
    X, y, merged = load_data(threshold=1.0)
    clf = train_random_forest(X, y)
    evaluate_model(clf, X, y)

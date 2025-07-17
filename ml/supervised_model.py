# ml/supervised_model.py
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib


def load_data(feature_path="results/features.csv", label_path="results/strategy_summary.csv", label_metric="Sharpe Ratio", threshold=1.0):
    """
    Merge features and labels; binarize label into success/failure based on threshold.
    """
    features = pd.read_csv(feature_path)
    labels = pd.read_csv(label_path)

    merged = pd.merge(features, labels, on="Pair")
    merged["Success"] = (merged[label_metric] >= threshold).astype(int)

    X = merged.drop(columns=["Pair", label_metric, "Success"])
    y = merged["Success"]

    return X, y, merged


def train_random_forest(X, y, save_path="models/rf_model.pkl"):
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


if __name__ == "__main__":
    X, y, merged = load_data(threshold=1.0)
    clf = train_random_forest(X, y)
    evaluate_model(clf, X, y)

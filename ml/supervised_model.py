import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

GLOBAL_MODEL_PATH = "models/rf_model.pkl"
REGIME_MODEL_TEMPLATE = "models/rf_model_regime_{}.pkl"

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

def train_random_forest(X, y, save_path=GLOBAL_MODEL_PATH):
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    scores = cross_val_score(clf, X, y, cv=5)
    print(f"Cross-validated accuracy: {scores.mean():.4f}")

    clf.fit(X, y)
    joblib.dump(clf, save_path)
    print(f"[Saved] RandomForest model to {save_path}")
    return clf

def train_models_per_regime(merged_df, model_template=REGIME_MODEL_TEMPLATE):
    """
    Train one model per regime using stratified data.
    """
    regime_col = "Regime"
    if regime_col not in merged_df.columns:
        print("[Error] 'Regime' column not found in merged data.")
        return

    for regime in sorted(merged_df[regime_col].unique()):
        subset = merged_df[merged_df[regime_col] == regime]
        if len(subset) < 5:
            print(f"[Skip] Regime {regime} has too few samples ({len(subset)}). Skipping.")
            continue

        drop_cols = ["Pair", "Success", regime_col]
        label_col = "Success"
        feature_cols = [col for col in subset.columns if col not in drop_cols]

        X_regime = subset[feature_cols]
        y_regime = subset[label_col]

        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        scores = cross_val_score(clf, X_regime, y_regime, cv=5)
        print(f"Regime {regime} - CV Accuracy: {scores.mean():.4f}")

        clf.fit(X_regime, y_regime)
        model_path = model_template.format(regime)
        joblib.dump(clf, model_path)
        print(f"[Saved] Regime-specific model to {model_path}")

def evaluate_model(clf, X, y):
    y_pred = clf.predict(X)
    print("\nConfusion Matrix:")
    print(confusion_matrix(y, y_pred))
    print("\nClassification Report:")
    print(classification_report(y, y_pred))

def predict_success(features_df, model_path=GLOBAL_MODEL_PATH, use_regime_models=False):
    """
    Predict probability of success using:
    - one global model (default)
    - or one model per regime (if use_regime_models=True)
    """
    if use_regime_models:
        if "Regime" not in features_df.columns:
            print("[Warning] Regime column not found. Falling back to global model.")
            use_regime_models = False

    preds = []
    for idx, row in features_df.iterrows():
        try:
            X = row.drop(labels=["Pair", "Success"], errors="ignore")
            X = X.to_frame().T  # make 2D

            if use_regime_models:
                regime = int(row["Regime"])
                model_file = REGIME_MODEL_TEMPLATE.format(regime)
                if os.path.exists(model_file):
                    clf = joblib.load(model_file)
                else:
                    print(f"[Fallback] No model for regime {regime}, using global model.")
                    clf = joblib.load(model_path)
            else:
                clf = joblib.load(model_path)

            proba = clf.predict_proba(X)[:, 1][0]
        except Exception as e:
            print(f"[Error] Prediction failed for index {idx}: {e}")
            proba = 1.0  # optimistic fallback

        preds.append(proba)

    return pd.Series(preds, index=features_df.index)

if __name__ == "__main__":
    X, y, merged = load_data(threshold=1.0)
    clf = train_random_forest(X, y)
    evaluate_model(clf, X, y)

    # OPTIONAL: Train one model per regime
    train_models_per_regime(merged)

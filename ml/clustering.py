import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import joblib
import os

CLUSTER_MODEL_PATH = "models/kmeans_model.pkl"


def cluster_features(feature_path="results/features.csv", n_clusters=3, save_model=True, plot=False):
    df = pd.read_csv(feature_path)
    X = df.drop(columns=["Pair"], errors="ignore")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(X_scaled)
    df["Regime"] = clusters

    if save_model:
        joblib.dump(kmeans, CLUSTER_MODEL_PATH)
        print(f"[Saved] KMeans model to {CLUSTER_MODEL_PATH}")

    df.to_csv("results/features.csv", index=False)  # overwrite with regime
    print("[Saved] Cluster labels added to 'results/features.csv'")

    if plot:
        pca = PCA(n_components=2)
        reduced = pca.fit_transform(X_scaled)
        plt.figure(figsize=(8, 5))
        for label in np.unique(clusters):
            plt.scatter(
                reduced[clusters == label, 0],
                reduced[clusters == label, 1],
                label=f"Regime {label}"
            )
        plt.title("PCA Projection of Clusters")
        plt.xlabel("PC1")
        plt.ylabel("PC2")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    return df


if __name__ == "__main__":
    cluster_features(plot=True)

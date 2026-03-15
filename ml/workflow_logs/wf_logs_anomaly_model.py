from sentence_transformers import SentenceTransformer
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
import numpy as np
import pandas as pd
import hdbscan
from config.settings import USE_CACHED_EMBEDDINGS

model = None

def get_model():
    global model

    if model is None:
        model = SentenceTransformer("models/all-MiniLM-L6-v2")

    return model

def generate_embeddings(df):

    embeddings = get_model().encode(
        df["execution_log_text"].tolist(),
        show_progress_bar=True
    )

    df["embedding"] = embeddings.tolist()

    return df

def detect_log_anomalies(df):

    embeddings = np.array(df["embedding"].tolist())

    model = IsolationForest(
        n_estimators=200,
        contamination=0.01,
        random_state=42
    )
    
    model.fit(embeddings)


    df["anomaly"] = model.predict(embeddings)
    df["anomaly_score"] = model.decision_function(embeddings)

    return df


def cluster_logs(df):
    
    embeddings = np.array(df["embedding"].tolist())

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=8,
        metric="euclidean"
    )

    df["cluster_id"] = clusterer.fit_predict(embeddings)
    df["cluster_probability"] = clusterer.probabilities_

    return df

def group_anomalies(anomalies_df, reps_per_group=3):

    if anomalies_df.empty:
        return anomalies_df, pd.DataFrame()

    embeddings = np.array(anomalies_df["embedding"].tolist())

    n = len(anomalies_df)

    # automatic K selection
    k = int(np.sqrt(n / 2))
    k = max(2, min(k, 15))

    print(f"KMeans anomaly grouping with k={k}")

    kmeans = KMeans(
        n_clusters=k,
        random_state=42,
        n_init="auto"
    )

    group_ids = kmeans.fit_predict(embeddings)

    anomalies_df = anomalies_df.copy()
    anomalies_df["anomaly_group_id"] = group_ids

    representatives = []

    for group_id in np.unique(group_ids):

        group_mask = anomalies_df["anomaly_group_id"] == group_id
        group_embeddings = embeddings[group_mask]
        group_rows = anomalies_df[group_mask]
        centroid = kmeans.cluster_centers_[group_id]
        distances = np.linalg.norm(group_embeddings - centroid, axis=1)
        group_rows = group_rows.copy()
        group_rows["distance"] = distances
        closest = group_rows.nsmallest(reps_per_group, "distance")
        representatives.append(closest)
        
    representatives_df = pd.concat(representatives)

    return anomalies_df, representatives_df
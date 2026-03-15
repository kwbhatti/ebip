from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

def summarize_clusters(df):

    cluster_counts = df.groupby("cluster_id").size().reset_index(name="count")

    print("\nCluster Distribution")
    print(cluster_counts.sort_values("count", ascending=False))

    for cluster in sorted(df["cluster_id"].unique()):

        print("\n=================================")
        print(f"CLUSTER {cluster}")

        sample = df[df["cluster_id"] == cluster].head(3)

        for text in sample["execution_log_text"]:
            print("\nExample execution:")
            print(text[:400])

def extract_cluster_themes(df, analysis_run_id, top_n=5):

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=2000
    )

    tfidf_matrix = vectorizer.fit_transform(df["execution_log_text"])

    terms = vectorizer.get_feature_names_out()

    df = df.copy()
    df["row_index"] = range(len(df))

    cluster_summary = []

    cluster_groups = df.groupby("cluster_id")

    for cluster_id, group in cluster_groups:

        if cluster_id == -1:
            continue

        row_indices = group["row_index"].values

        cluster_matrix = tfidf_matrix[row_indices]

        mean_scores = cluster_matrix.mean(axis=0).A1

        top_indices = mean_scores.argsort()[-top_n:][::-1]

        top_terms = [terms[i] for i in top_indices]

        cluster_summary.append({
            "analysis_run_id": analysis_run_id,
            "cluster_id": cluster_id,
            "cluster_size": len(group),
            "cluster_theme": ", ".join(top_terms)
        })

    
    cluster_summary_df = pd.DataFrame(cluster_summary)

    if cluster_summary_df.empty:
        cluster_summary_df = pd.DataFrame(
            columns=["analysis_run_id", "cluster_id", "cluster_size", "cluster_theme"]
        )
    return cluster_summary_df

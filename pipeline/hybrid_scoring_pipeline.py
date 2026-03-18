import uuid
from datetime import datetime
from db.sqlite_store import load_latest_wf_exe_anomalies, load_latest_wf_logs_clusters, save_wf_exe_logs_hybrid_scores

def run_hybrid_scoring_pipeline():

    print("loading wf_exe_anomalies table")
    wf_exe_anomalies = load_latest_wf_exe_anomalies()
    print("loading wf_logs_clusters table")
    wf_logs_clusters = load_latest_wf_logs_clusters()

    df_exec = wf_exe_anomalies.copy()

    print("setting structured score for execution anomalies")
    # min_score = df_exec["anomaly_score"].min()
    # max_score = df_exec["anomaly_score"].max()

    # df_exec["structured_score"] = (
    #     (df_exec["anomaly_score"] - min_score) /
    #     (max_score - min_score)
    # )

    df_exec["structured_score"] = df_exec["anomaly_score"].rank(pct=True)
    df_exec.loc[df_exec["anomaly"] == -1, "structured_score"] = 1

    df_logs = wf_logs_clusters.copy()

    print("setting semantic score for log clusters")
    df_logs["semantic_score"] = 1 - df_logs["cluster_probability"]

    print("merging both data frames while keeping all logs info using left join")
    df_joined = df_logs.merge(
        df_exec[["job_instance_id", "structured_score"]],
        on="job_instance_id",
        how="left"
    )

    run_id = str(uuid.uuid4())    
    scored_at = datetime.now()

    df_joined["analysis_run_id"] = run_id
    df_joined["scored_at"] = scored_at
    print(f"run_id: {run_id}")

    df_joined["structured_score"] = df_joined["structured_score"].fillna(0)

    print("assinging hybrid score")
    df_joined["hybrid_score"] = (
        0.7 * df_joined["structured_score"] +
        0.3 * df_joined["semantic_score"]
    )

    df_joined.loc[df_joined["semantic_score"] > 0.9, "hybrid_score"] = (
        df_joined["hybrid_score"] + 0.3
    ).clip(0, 1)
    
    

    save_wf_exe_logs_hybrid_scores(df_joined)
    # print(df_joined.head(20))
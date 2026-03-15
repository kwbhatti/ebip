import uuid
from datetime import datetime
from db.sql_server import load_wf_logs_data
from features.workflow_logs.wf_logs_features import clean_log_messages, group_logs_by_execution, build_execution_log_text
from ml.workflow_logs.wf_logs_anomaly_model import generate_embeddings, cluster_logs, group_anomalies
from db.sqlite_store import (
    save_wf_logs_embeddings, 
    load_wf_logs_embeddings, 
    save_wf_logs_clusters, 
    save_wf_logs_cluster_summary, 
    load_wf_logs_cluster_summary, 
    save_wf_logs_cluster_anomalies,
    save_wf_logs_cluster_anomalies_grouped
)
from ml.workflow_logs.wf_logs_explanations import extract_cluster_themes
from ai.workflow_logs.wf_logs_ai_explanations import build_ai_prompt, analyze_clusters
from config.settings import USE_CACHED_EMBEDDINGS, USE_CACHED_CLUSTER_SUMMARY

# grouped_logs_df = detect_log_anomalies(grouped_logs_df)
# summarize_clusters(grouped_logs_df)

def run_wf_logs_pipeline():

    print("Executing workflow logs pipeline")
    print("Extracting data from IND database")
    logs_df = load_wf_logs_data()
    # logs_df = job_instance_id, job_id, job_name, job_description, log_text, date
    print("Found total number of logs: %d", len(logs_df))
    logs_df = clean_log_messages(logs_df)
    # logs_df = job_instance_id, job_id, job_name, job_description, log_text, date, clean_log
    grouped_logs_df = group_logs_by_execution(logs_df)
    # grouped_logs_df = job_instance_id(grouped by), job_id, job_name, job_description, clean_log(list)
    grouped_logs_df = build_execution_log_text(grouped_logs_df)
    # grouped_logs_df = job_instance_id(grouped by), job_id, job_name, job_description, clean_log(list), 
    #   execution_log_text(clean_log list to string)
    if USE_CACHED_EMBEDDINGS:
        print("using cached embeddings")
        grouped_logs_df = load_wf_logs_embeddings()
    else:
        print("generating embeddings")
        grouped_logs_df = generate_embeddings(grouped_logs_df)
        save_wf_logs_embeddings(grouped_logs_df)
    # grouped_logs_df = job_instance_id(grouped by), job_id, job_name, job_description, clean_log(list), 
    #   execution_log_text(clean_log list to string), embeddings(list)
    
    grouped_logs_df = cluster_logs(grouped_logs_df)
    # grouped_logs_df = job_instance_id(grouped by), job_id, job_name, job_description, clean_log(list), 
    #   execution_log_text(clean_log list to string), embeddings(list), cluster_id, cluster_probability

    run_id = str(uuid.uuid4())    
    scored_at = datetime.now()

    print(f"run_id: {run_id}")

    grouped_logs_df["analysis_run_id"] = run_id
    grouped_logs_df["scored_at"] = scored_at
    # grouped_logs_df = job_instance_id(grouped by), job_id, job_name, job_description, clean_log(list), 
    #   execution_log_text(clean_log list to string), embeddings(list), cluster_id, cluster_probability, 
    #   analysis_run_id, scored_at

    save_wf_logs_clusters(grouped_logs_df)

    cluster_summary_df = None
    if USE_CACHED_CLUSTER_SUMMARY:
        cluster_summary_df = load_wf_logs_cluster_summary()
    else:
        cluster_summary_df = extract_cluster_themes(grouped_logs_df, run_id)
        save_wf_logs_cluster_summary(cluster_summary_df)
    # cluster_summary_df = analysis_run_id, cluster_id, cluster_size, cluster_theme
    
    anomalies_df = grouped_logs_df[grouped_logs_df["cluster_id"] == -1].copy()
    # anomalies_df = job_instance_id(grouped by), job_id, job_name, job_description, clean_log(list), 
    #   execution_log_text(clean_log list to string), embeddings(list), cluster_id, cluster_probability, 
    #   analysis_run_id, scored_at
    anomalies_df["log_length"] = anomalies_df["execution_log_text"].str.len()
    # anomalies_df = job_instance_id(grouped by), job_id, job_name, job_description, clean_log(list), 
    #   execution_log_text(clean_log list to string), embeddings(list), cluster_id, cluster_probability, 
    #   analysis_run_id, scored_at, log_length
    anomalies_df["log_count"] = anomalies_df["clean_log"].apply(len)
    # anomalies_df = job_instance_id(grouped by), job_id, job_name, job_description, clean_log(list), 
    #   execution_log_text(clean_log list to string), embeddings(list), cluster_id, cluster_probability, 
    #   analysis_run_id, scored_at, log_length, log_count
    save_wf_logs_cluster_anomalies(anomalies_df)

    anomalies_df, anomaly_representatives = group_anomalies(anomalies_df)


    # anomalies_df = job_instance_id(grouped by), job_id, job_name, job_description, clean_log(list), 
    #   execution_log_text(clean_log list to string), embeddings(list), cluster_id, cluster_probability, 
    #   analysis_run_id, scored_at, log_length, log_count, anomaly_group_id

    save_wf_logs_cluster_anomalies_grouped(anomalies_df)
    
    # prompt = build_ai_prompt(
    #     grouped_logs_df["job_name"].iloc[0],
    #     grouped_logs_df["job_description"].iloc[0],
    #     cluster_summary_df,
    #     anomalies_df
    # )

    # analysis = analyze_clusters(prompt)

    # print(analysis)

    print(anomalies_df["anomaly_group_id"].value_counts())
    return logs_df

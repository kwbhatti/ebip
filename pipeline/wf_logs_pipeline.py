from db.sql_server import load_wf_logs_data
from features.workflow_logs.wf_logs_features import clean_log_messages, group_logs_by_execution, build_execution_log_text
from ml.workflow_logs.wf_logs_anomaly_model import generate_embeddings

def run_wf_logs_pipeline():

    logs_df = load_wf_logs_data()

    logs_df = clean_log_messages(logs_df)

    grouped_logs_df = group_logs_by_execution(logs_df)

    grouped_logs_df = build_execution_log_text(grouped_logs_df)

    grouped_logs_df = generate_embeddings(grouped_logs_df)

    print("Total logs:", len(logs_df))
    print("Total grouped_logs:", len(grouped_logs_df))

    print(logs_df[["str_log", "clean_log"]].head(10))
    print(grouped_logs_df[["int_job_instance_id", "execution_log_text"]].head())
    print(grouped_logs_df.head())
    return logs_df
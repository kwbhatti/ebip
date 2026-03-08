from datetime import datetime
import uuid
from db.sql_server import load_execution_data
from db.sqlite_store import save_results
from features.workflow_execution.wf_exe_features import build_features, extract_feature_matrix
from ml.workflow_execution.wf_exe_anomaly_model import scale_features
from ml.workflow_execution.wf_exe_anomaly_model import score_executions
from ml.workflow_execution.wf_exe_explanations import generate_anomaly_reasons

def run_execution_pipeline():

    df = load_execution_data()

    df = build_features(df)

    X = extract_feature_matrix(df)

    X_scaled = scale_features(df)

    df = score_executions(df, X_scaled)

    run_id = str(uuid.uuid4())    
    scored_at = datetime.now()

    df["analysis_run_id"] = run_id
    df["scored_at"] = scored_at

    df = generate_anomaly_reasons(df)

    save_results(df)

    return df
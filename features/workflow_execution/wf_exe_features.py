def build_features(df):
    df["execution_gap_seconds"] = (
        df["job_duration_seconds"] - df["total_step_duration"]
    )
    return df

def extract_feature_matrix(df):
    return df.drop(columns=["job_instance_id"])
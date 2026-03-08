def explain_anomaly(row):
    reasons = []

    if row["retry_count"] > 0:
        reasons.append("step retries detected")

    if row["failed_step_count"] > 0:
        reasons.append("failed steps present")

    if row["job_duration_seconds"] > 300:
        reasons.append("long execution duration")

    if row["max_step_duration"] > 60:
        reasons.append("slow step detected")

    if row["step_count"] > 20:
        reasons.append("high step count")

    if not reasons:
        reasons.append("statistical anomaly")

    return ", ".join(reasons)


def generate_anomaly_reasons(df):
    df["anomaly_reason"] = None

    df.loc[df["anomaly"] == -1, "anomaly_reason"] = (
        df[df["anomaly"] == -1].apply(explain_anomaly, axis=1)
    )

    return df
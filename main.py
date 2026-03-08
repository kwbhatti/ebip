import pyodbc
import pandas as pd
from sklearn.ensemble import IsolationForest  # anomaly detection model
import sqlite3
from datetime import datetime
import uuid
from sklearn.preprocessing import StandardScaler

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

# open connection to SQL Server
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=2228-IND-2;"
    "UID=sa;"
    "PWD=HippityHoppitus9!;"
)

query = """
SELECT
    ji.int_job_instance_id,

    -- total job duration
    DATEDIFF(SECOND, ji.dte_start_time, ji.dte_end_time) AS job_duration_seconds,

    -- number of step executions
    COUNT(jsi.int_job_step_instance_id) AS step_count,

    -- retries (same step executed multiple times)
    COUNT(jsi.int_job_step_instance_id)
        - COUNT(DISTINCT jsi.int_job_step_id) AS retry_count,

    -- failed steps
    SUM(CASE
        WHEN jsi.str_status = 'Failed' THEN 1
        ELSE 0
    END) AS failed_step_count,

    -- step duration metrics
    COALESCE(
        AVG(DATEDIFF(SECOND, jsi.dte_start_time, jsi.dte_end_time)),
        0
    ) AS avg_step_duration,

    MAX(DATEDIFF(SECOND, jsi.dte_start_time, jsi.dte_end_time)) AS max_step_duration,

    COALESCE(
        STDEV(DATEDIFF(SECOND, jsi.dte_start_time, jsi.dte_end_time)),
        0
    ) AS step_duration_stddev,

    SUM(
        DATEDIFF(SECOND, jsi.dte_start_time, jsi.dte_end_time)
    ) AS total_step_duration

FROM Job_Instances ji
JOIN Job_Step_Instances jsi
    ON ji.int_job_instance_id = jsi.int_job_instance_id

WHERE
    ji.dte_end_time IS NOT NULL
    AND jsi.dte_end_time IS NOT NULL

GROUP BY
    ji.int_job_instance_id,
    ji.dte_start_time,
    ji.dte_end_time
"""

# executes the SQL query and loads the result into a pandas DataFrame
df = pd.read_sql(query, conn)
df["execution_gap_seconds"] = (
    df["job_duration_seconds"] - df["total_step_duration"]
)
# remove identifier column (not useful for ML)
X = df.drop(columns=["int_job_instance_id"])
# show first few rows of the feature matrix
# print(X.head())
# prints the total number of rows returned by the query
# print("Rows:", len(X))
# show column names and data types
# print("\nColumn Types:")
# print(X.dtypes)
# show basic statistics for numeric columns
# print("\nBasic Statistics:")
# print(X.describe())
# create the Isolation Forest model
model = IsolationForest(
    n_estimators=100,   # number of trees used to detect anomalies
    contamination=0.01, # expected % of anomalies (1% is a good starting guess)
    random_state=42     # keeps results consistent each run
)
scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)

# train the model using the feature matrix
model.fit(X_scaled)

# generate anomaly predictions
df["anomaly"] = model.predict(X_scaled)

# generate anomaly score (how unusual each job is)
df["anomaly_score"] = model.decision_function(X_scaled)

# show the most suspicious executions
print(df.sort_values("anomaly_score").head(20))

# create (or open) EBIP sqlite database

conn = sqlite3.connect("ebip.db")
# save anomaly results into SQLite table

run_id = str(uuid.uuid4())
scored_at = datetime.now()
df["analysis_run_id"] = run_id
df["scored_at"] = scored_at

df["anomaly_reason"] = None

df.loc[df["anomaly"] == -1, "anomaly_reason"] = (
    df[df["anomaly"] == -1].apply(explain_anomaly, axis=1)
)
df.to_sql("execution_anomalies", conn, if_exists="replace", index=False)

conn.close()


import sqlite3
from config.settings import SQLITE_DB_PATH

def save_results(df):

    conn = sqlite3.connect(SQLITE_DB_PATH)
    df.to_sql(
        "execution_anomalies",
        conn,
        if_exists="append",
        index=False
    )

    conn.close()
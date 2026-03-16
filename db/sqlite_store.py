import sqlite3
import json
import pandas as pd
from config.settings import SQLITE_DB_PATH

def save_wf_exe_results(df):

    conn = sqlite3.connect(SQLITE_DB_PATH)
    df.to_sql(
        "execution_anomalies",
        conn,
        if_exists="append",
        index=False
    )

    conn.close()

def save_wf_logs_embeddings(df):

    df_copy = df.copy(deep=True)

    df_copy["clean_log"] = df_copy["clean_log"].apply(json.dumps)
    df_copy["embedding"] = df_copy["embedding"].apply(json.dumps)

    conn = sqlite3.connect(SQLITE_DB_PATH)

    df_copy.to_sql(
        "wf_log_embeddings",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

def load_wf_logs_embeddings():

    conn = sqlite3.connect(SQLITE_DB_PATH)

    df = pd.read_sql(
        "SELECT * FROM wf_log_embeddings",
        conn
    )

    conn.close()
    df["clean_log"] = df["clean_log"].apply(json.loads)
    df["embedding"] = df["embedding"].apply(json.loads)
    return df

def save_log_anomalies(df):
    df_copy = df.copy(deep=True)

    df_copy["clean_log"] = df_copy["clean_log"].apply(json.dumps)
    df_copy["embedding"] = df_copy["embedding"].apply(json.dumps)
    conn = sqlite3.connect(SQLITE_DB_PATH)
    df_copy.to_sql(
        "wf_logs_anomalies",
        conn,
        if_exists="append",
        index=False
    )

    conn.close()


def save_wf_logs_clusters(df):

    df_copy = df.copy(deep=True)

    df_copy["clean_log"] = df_copy["clean_log"].apply(json.dumps)
    df_copy["embedding"] = df_copy["embedding"].apply(json.dumps)
    conn = sqlite3.connect(SQLITE_DB_PATH)
    df_copy.to_sql(
        "wf_logs_clusters",
        conn,
        if_exists="append",
        index=False
    )

    conn.close()

def save_wf_logs_cluster_anomalies(df):

    df_copy = df.copy(deep=True)

    df_copy["clean_log"] = df_copy["clean_log"].apply(json.dumps)
    df_copy["embedding"] = df_copy["embedding"].apply(json.dumps)
    conn = sqlite3.connect(SQLITE_DB_PATH)
    df_copy.to_sql(
        "wf_logs_cluster_anomalies",
        conn,
        if_exists="append",
        index=False
    )

    conn.close()

def save_wf_logs_cluster_summary(df):

    conn = sqlite3.connect(SQLITE_DB_PATH)

    df.to_sql(
        "wf_logs_cluster_summary",
        conn,
        if_exists="append",
        index=False
    )

    conn.close()

def load_wf_logs_cluster_summary():

    conn = sqlite3.connect(SQLITE_DB_PATH)

    df = pd.read_sql(
        "SELECT * FROM wf_logs_cluster_summary",
        conn
    )

    conn.close()
    return df

def save_wf_logs_cluster_anomalies_grouped(df):

    df_copy = df.copy(deep=True)

    df_copy["clean_log"] = df_copy["clean_log"].apply(json.dumps)
    df_copy["embedding"] = df_copy["embedding"].apply(json.dumps)
    conn = sqlite3.connect(SQLITE_DB_PATH)
    df_copy.to_sql(
        "wf_logs_cluster_anomalies_grouped",
        conn,
        if_exists="append",
        index=False
    )

    conn.close()

import pyodbc
import pandas as pd
from config.settings import SQL_SERVER_CONNECTION
from db.queries import EXECUTION_FEATURE_QUERY, WF_LOGS_QUERY

def get_connection():
    return pyodbc.connect(SQL_SERVER_CONNECTION)

def load_wf_exe_data():
    conn = get_connection()

    df = pd.read_sql(EXECUTION_FEATURE_QUERY, conn)    
    conn.close()

    return df

def load_wf_logs_data():
    conn = get_connection()
    df = pd.read_sql(WF_LOGS_QUERY, conn)
    conn.close()
    return df
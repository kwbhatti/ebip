def clean_log_messages(df):

    df["clean_log"] = df["str_log"]

    # remove leading timestamps
    df["clean_log"] = df["clean_log"].str.replace(
        r"\d{2}/\d{2}/\d{2}.*?:", "", regex=True
    )

    # remove HTML tags like <BR>
    df["clean_log"] = df["clean_log"].str.replace(
        r"<.*?>", "", regex=True
    )

    # normalize whitespace
    df["clean_log"] = df["clean_log"].str.replace(
        r"\s+", " ", regex=True
    ).str.strip()

    return df

def group_logs_by_execution(df):

    grouped = (
        df.groupby("int_job_instance_id")["clean_log"]
        .apply(list)
        .reset_index()
    )

    return grouped

def build_execution_log_text(grouped_logs_df):

    grouped_logs_df["execution_log_text"] = grouped_logs_df["clean_log"].apply(
        lambda logs: " ".join(logs)
    )

    return grouped_logs_df
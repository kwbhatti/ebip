import boto3
import json

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

# will not be using this for now since it is not that great
def build_ai_prompt(job_name, job_description, cluster_summary_df, anomalies_df):

    cluster_info = "\n".join(
        f"Cluster {row.cluster_id} → {row.cluster_size} executions → {row.cluster_theme}"
        for _, row in cluster_summary_df.iterrows()
    )

    anomaly_examples = "\n\n".join(
        anomalies_df["execution_log_text"].head(20).tolist()
    )

    prompt = f"""
    Workflow: {job_name}
    Description: {job_description}

    Cluster Distribution and Themes:
    {cluster_info}

    Anomalous Executions:
    {anomaly_examples}

    Explain:
    1. What anomaly behavior appears to be happening
    2. Possible operational causes
    3. Whether this indicates instability or expected system behavior
    """

    return prompt

# will not be using this for now since it is not that great
def analyze_clusters(prompt):

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 500,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })

    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        body=body,
        contentType="application/json",
        accept="application/json"
    )

    result = json.loads(response["body"].read())

    return result["content"][0]["text"]
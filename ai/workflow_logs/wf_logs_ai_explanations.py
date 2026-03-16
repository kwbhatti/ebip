import boto3
import json

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

import json

MAX_EXECUTIONS = 10
MAX_LOG_CHARS = 4000


def build_ai_prompt(anomaly_group_df):

    executions = []

    subset = anomaly_group_df.head(MAX_EXECUTIONS)

    for _, row in subset.iterrows():

        executions.append({
            "execution_id": str(row["job_instance_id"]),
            "log_text": row["execution_log_text"][:MAX_LOG_CHARS]
        })

    executions_json = json.dumps(executions, indent=2)

    prompt = f"""
    You are analyzing system execution logs that show unusual behavior.

    Identify the pattern shared by these executions and evaluate each execution.

    RULES:
    - Return JSON only.
    - Do not include explanations.
    - pattern_summary <= 12 words
    - possible_cause <= 8 words
    - risk_score 0-100
    - confidence 0-100

    JSON FORMAT:

    {{
    "pattern_summary": "",
    "risk_score": 0,
    "rows": [
        {{
        "execution_id": "",
        "possible_cause": "",
        "concerning": true,
        "confidence": 0
        }}
    ]
    }}

    Executions:
    {executions_json}
    """

    return prompt

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
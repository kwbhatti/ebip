EXECUTION_FEATURE_QUERY = """
SELECT
    ji.int_job_instance_id,

    DATEDIFF(SECOND, ji.dte_start_time, ji.dte_end_time) AS job_duration_seconds,

    COUNT(jsi.int_job_step_instance_id) AS step_count,

    COUNT(jsi.int_job_step_instance_id)
        - COUNT(DISTINCT jsi.int_job_step_id) AS retry_count,

    SUM(CASE
        WHEN jsi.str_status = 'Failed' THEN 1
        ELSE 0
    END) AS failed_step_count,

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
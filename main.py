from pipeline.wf_exe_pipeline import run_wf_exe_pipeline
from pipeline.wf_logs_pipeline import run_wf_logs_pipeline
from pipeline.hybrid_scoring_pipeline import run_hybrid_scoring_pipeline

def main():

    # wf_exe_df = run_wf_exe_pipeline()

    # print(wf_exe_df.sort_values("anomaly_score").head(20))

    # wf_logs_df = run_wf_logs_pipeline()

    run_hybrid_scoring_pipeline()

if __name__ == "__main__":
    main()
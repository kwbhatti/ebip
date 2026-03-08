from pipeline.wf_exe_pipeline import run_execution_pipeline


def main():

    df = run_execution_pipeline()

    print(df.sort_values("anomaly_score").head(20))


if __name__ == "__main__":
    main()
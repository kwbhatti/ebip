from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embeddings(df):

    embeddings = model.encode(
        df["execution_log_text"].tolist(),
        show_progress_bar=True
    )

    df["embedding"] = list(embeddings)

    return df
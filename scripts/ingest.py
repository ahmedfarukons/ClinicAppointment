"""
ChatDoctor dataset ingestion script.

Downloads the dataset from Kaggle (JSON), chunks the doctor-patient
dialogues, embeds them with sentence-transformers, and stores them in a
local Qdrant collection.

Usage:
    python -m scripts.ingest                            # auto-download from Kaggle
    python -m scripts.ingest --csv data/chatdoctor.csv  # local CSV
    python -m scripts.ingest --limit 200                # quick test with 200 rows
"""

import argparse
import glob
import json
import os

import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

from app.config import settings


def load_dataframe(csv_path: str | None) -> pd.DataFrame:
    if csv_path:
        if csv_path.endswith(".json"):
            return pd.read_json(csv_path)
        return pd.read_csv(csv_path)

    import kagglehub

    path = kagglehub.dataset_download("punyaslokaprusty/chatdoctor")
    print(f"Kaggle dataset downloaded to: {path}")

    json_files = glob.glob(os.path.join(path, "**", "*.json"), recursive=True)
    csv_files = glob.glob(os.path.join(path, "**", "*.csv"), recursive=True)

    all_files = json_files + csv_files
    if not all_files:
        raise FileNotFoundError(f"No data files found in {path}")

    print(f"Found data files: {all_files}")

    frames = []
    for f in all_files:
        print(f"  Loading {os.path.basename(f)} …")
        if f.endswith(".json"):
            with open(f, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
            frames.append(pd.DataFrame(raw))
        else:
            frames.append(pd.read_csv(f))

    return pd.concat(frames, ignore_index=True)


def _detect_columns(df: pd.DataFrame) -> tuple[str, str]:
    """Auto-detect patient question and doctor answer columns."""
    patient_col = None
    doctor_col = None

    patient_candidates = ["input", "patient", "question", "instruction"]
    doctor_candidates = [
        "output", "answer_chatdoctor", "answer_icliniq",
        "doctor", "answer", "response",
    ]

    cols_lower = {c.lower().strip(): c for c in df.columns}

    for cand in patient_candidates:
        if cand in cols_lower:
            patient_col = cols_lower[cand]
            break

    for cand in doctor_candidates:
        if cand in cols_lower:
            doctor_col = cols_lower[cand]
            break

    if not patient_col or not doctor_col:
        raise ValueError(
            f"Could not auto-detect columns. Available: {list(df.columns)}"
        )

    return patient_col, doctor_col


def chunk_dialogues(
    df: pd.DataFrame,
    chunk_size: int = settings.chunk_size,
    overlap: int = settings.chunk_overlap,
) -> list[dict]:
    patient_col, doctor_col = _detect_columns(df)
    print(f"Using columns: patient={patient_col}, doctor={doctor_col}")

    chunks: list[dict] = []
    for idx, row in df.iterrows():
        patient_q = str(row[patient_col])
        doctor_a = str(row[doctor_col])

        if doctor_a in ("nan", "", "None") or pd.isna(row[doctor_col]):
            continue

        text = f"Patient: {patient_q}\nDoctor: {doctor_a}"

        if len(text) <= chunk_size:
            chunks.append({"text": text, "source_row": int(idx), "chunk_idx": 0})
        else:
            words = text.split()
            step = max(1, chunk_size // 5)
            overlap_words = max(1, overlap // 5)
            start = 0
            ci = 0
            while start < len(words):
                end = start + step
                segment = " ".join(words[start:end])
                chunks.append({"text": segment, "source_row": int(idx), "chunk_idx": ci})
                start = end - overlap_words
                ci += 1
    return chunks


def embed_and_store(chunks: list[dict]) -> None:
    print(f"Loading embedding model: {settings.embedding_model}")
    model = SentenceTransformer(settings.embedding_model)

    texts = [c["text"] for c in chunks]
    print(f"Embedding {len(texts)} chunks …")
    vectors = model.encode(texts, show_progress_bar=True, batch_size=128)

    dim = vectors.shape[1]
    print(f"Embedding dimension: {dim}")

    qdrant = QdrantClient(path=settings.qdrant_path)

    if qdrant.collection_exists(settings.collection_name):
        qdrant.delete_collection(settings.collection_name)

    qdrant.create_collection(
        collection_name=settings.collection_name,
        vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
    )

    points = [
        PointStruct(
            id=i,
            vector=vectors[i].tolist(),
            payload={
                "text": chunks[i]["text"],
                "source_row": chunks[i]["source_row"],
                "chunk_idx": chunks[i]["chunk_idx"],
            },
        )
        for i in range(len(chunks))
    ]

    batch_size = 256
    for start in range(0, len(points), batch_size):
        batch = points[start : start + batch_size]
        qdrant.upsert(collection_name=settings.collection_name, points=batch)
        print(f"  upserted {start + len(batch)}/{len(points)}")

    print(f"Ingestion complete. Total points: {len(points)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest ChatDoctor dataset into Qdrant")
    parser.add_argument("--csv", type=str, default=None, help="Path to local CSV or JSON file")
    parser.add_argument("--limit", type=int, default=None, help="Limit rows for quick testing")
    args = parser.parse_args()

    df = load_dataframe(args.csv)
    if args.limit:
        df = df.head(args.limit)
    print(f"Loaded {len(df)} rows. Columns: {list(df.columns)}")

    chunks = chunk_dialogues(df)
    print(f"Created {len(chunks)} chunks.")

    embed_and_store(chunks)


if __name__ == "__main__":
    main()

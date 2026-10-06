from pathlib import Path
import json

import faiss
import numpy as np

from app.rag.chunker import DocumentChunk


class PolicyVectorStore:

    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.index = None
        self.metadata = []

    def build(
        self,
        chunks: list[DocumentChunk],
        embeddings,
    ):
        if not chunks:
            raise ValueError(
                "Cannot build vector store without chunks"
            )

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks and embeddings must match"
            )

        embeddings = np.asarray(
            embeddings,
            dtype="float32",
        )

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dimension)

        self.index.add(embeddings)

        self.metadata = [
            {
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "source": chunk.source,
            }
            for chunk in chunks
        ]

    def save(self):
        if self.index is None:
            raise ValueError(
                "Vector store has not been built"
            )

        self.storage_path.mkdir(
            parents=True,
            exist_ok=True,
        )

        index_path = self.storage_path / "index.faiss"
        metadata_path = self.storage_path / "metadata.json"

        faiss.write_index(
            self.index,
            str(index_path),
        )

        metadata_path.write_text(
            json.dumps(
                self.metadata,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def load(self):
        index_path = self.storage_path / "index.faiss"
        metadata_path = self.storage_path / "metadata.json"

        if not index_path.exists():
            raise FileNotFoundError(
                f"FAISS index not found: {index_path}"
            )

        if not metadata_path.exists():
            raise FileNotFoundError(
                f"Metadata not found: {metadata_path}"
            )

        self.index = faiss.read_index(
            str(index_path)
        )

        self.metadata = json.loads(
            metadata_path.read_text(
                encoding="utf-8"
            )
        )

    def search(
        self,
        query_embedding,
        top_k: int = 5,
    ) -> list[dict]:

        if self.index is None:
            raise ValueError(
                "Vector store is not loaded"
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero"
            )

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32",
        )

        scores, indices = self.index.search(
            query_embedding,
            min(top_k, self.index.ntotal),
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):
            if index < 0:
                continue

            item = self.metadata[index].copy()

            item["score"] = float(score)

            results.append(item)

        return results
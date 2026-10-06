import numpy as np

from app.rag.chunker import DocumentChunk
from app.rag.vector_store import PolicyVectorStore


def test_vector_store_build_and_search(tmp_path):

    chunks = [
        DocumentChunk(
            chunk_id=0,
            text="Casual Leave is 12 days.",
            source="leave_policy.txt",
        ),
        DocumentChunk(
            chunk_id=1,
            text="Earned Leave is 8 days.",
            source="leave_policy.txt",
        ),
        DocumentChunk(
            chunk_id=2,
            text="Maternity Leave is 26 weeks.",
            source="leave_policy.txt",
        ),
    ]

    embeddings = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype="float32",
    )

    store = PolicyVectorStore(
        str(tmp_path)
    )

    store.build(
        chunks,
        embeddings,
    )

    results = store.search(
        np.array(
            [[1.0, 0.0, 0.0]],
            dtype="float32",
        ),
        top_k=1,
    )

    assert len(results) == 1

    assert (
        results[0]["text"]
        == "Casual Leave is 12 days."
    )


def test_vector_store_save_and_load(tmp_path):

    chunks = [
        DocumentChunk(
            chunk_id=0,
            text="CL cannot be carried forward.",
            source="leave_policy.txt",
        )
    ]

    embeddings = np.array(
        [[1.0, 0.0]],
        dtype="float32",
    )

    store = PolicyVectorStore(
        str(tmp_path)
    )

    store.build(
        chunks,
        embeddings,
    )

    store.save()

    new_store = PolicyVectorStore(
        str(tmp_path)
    )

    new_store.load()

    results = new_store.search(
        np.array(
            [[1.0, 0.0]],
            dtype="float32",
        ),
        top_k=1,
    )

    assert len(results) == 1

    assert (
        results[0]["text"]
        == "CL cannot be carried forward."
    )
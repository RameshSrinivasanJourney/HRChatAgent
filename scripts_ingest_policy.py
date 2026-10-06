from pathlib import Path

from app.rag.loader import PolicyDocumentLoader
from app.rag.chunker import PolicyChunker
from app.rag.embeddings import PolicyEmbeddingService
from app.rag.vector_store import PolicyVectorStore


BASE_DIR = Path(__file__).resolve().parent

POLICY_PATH = (
    BASE_DIR / "documents" / "leave_policy.txt"
)

VECTOR_STORE_PATH = (
    BASE_DIR / "vectorstore" / "policy"
)


def main():

    print("=" * 60)
    print("HR POLICY KNOWLEDGE BASE INGESTION")
    print("=" * 60)

    # 1. Load
    print("\n[1/4] Loading policy document...")

    loader = PolicyDocumentLoader()

    policy_text = loader.load(
        str(POLICY_PATH)
    )

    print(
        f"Loaded {len(policy_text)} characters."
    )

    # 2. Chunk
    print("\n[2/4] Creating document chunks...")

    chunker = PolicyChunker(
        chunk_size=800,
        chunk_overlap=120,
    )

    chunks = chunker.split(
        policy_text,
        source="leave_policy.txt",
    )

    print(
        f"Created {len(chunks)} chunks."
    )

    # 3. Embeddings
    print("\n[3/4] Creating embeddings...")

    embedding_service = (
        PolicyEmbeddingService()
    )

    embeddings = (
        embedding_service.embed_documents(
            [chunk.text for chunk in chunks]
        )
    )

    print(
        f"Embedding shape: {embeddings.shape}"
    )

    # 4. FAISS
    print("\n[4/4] Building FAISS index...")

    vector_store = PolicyVectorStore(
        str(VECTOR_STORE_PATH)
    )

    vector_store.build(
        chunks,
        embeddings,
    )

    vector_store.save()

    print("\n" + "=" * 60)
    print("POLICY INGESTION COMPLETED")
    print("=" * 60)

    print(
        f"Vector store: {VECTOR_STORE_PATH}"
    )


if __name__ == "__main__":
    main()
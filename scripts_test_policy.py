from pathlib import Path

from app.rag.embeddings import PolicyEmbeddingService
from app.rag.vector_store import PolicyVectorStore
from app.rag.retriever import PolicyRetriever


BASE_DIR = Path(__file__).resolve().parent

VECTOR_STORE_PATH = (
    BASE_DIR / "vectorstore" / "policy"
)


def main():

    print("=" * 70)
    print("HR POLICY RETRIEVAL TEST")
    print("=" * 70)

    embedding_service = (
        PolicyEmbeddingService()
    )

    vector_store = PolicyVectorStore(
        str(VECTOR_STORE_PATH)
    )

    vector_store.load()

    retriever = PolicyRetriever(
        embedding_service,
        vector_store,
    )

    questions = [
        "How many casual leaves do employees get?",
        "Can casual leave be carried forward?",
        "What happens when earned leave reaches 20 days?",
        "How does PL conversion to EL work?",
        "How many weeks of maternity leave are available?",
        "How many days of paternity leave are available?",
        "How do I apply for leave?",
        "Are holidays counted during approved leave?",
        "What happens if I don't apply for leave?",
    ]

    for number, question in enumerate(
        questions,
        start=1,
    ):

        print("\n" + "-" * 70)
        print(f"QUESTION {number}")
        print("-" * 70)

        print(question)

        results = retriever.retrieve(
            question,
            top_k=3,
        )

        for index, result in enumerate(
            results,
            start=1,
        ):

            print(
                f"\nResult {index}"
            )

            print(
                f"Score: {result['score']:.4f}"
            )

            print(
                result["text"]
            )


if __name__ == "__main__":
    main()
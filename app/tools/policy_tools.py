from pathlib import Path

from app.rag.embeddings import PolicyEmbeddingService
from app.rag.vector_store import PolicyVectorStore
from app.rag.retriever import PolicyRetriever


BASE_DIR = Path(__file__).resolve().parents[2]

VECTOR_STORE_PATH = (
    BASE_DIR / "vectorstore" / "policy"
)


class PolicySearchTool:

    def __init__(
        self,
        retriever: PolicyRetriever,
    ):
        self.retriever = retriever

    def search(
        self,
        question: str,
        top_k: int = 5,
    ) -> str:

        results = self.retriever.retrieve(
            question,
            top_k=top_k,
        )

        if not results:
            return (
                "No relevant HR policy information "
                "was found."
            )

        output = []

        for result in results:
            output.append(
                f"[Source: {result['source']}]\n"
                f"{result['text']}"
            )

        return "\n\n---\n\n".join(output)


def create_policy_search_tool():

    embedding_service = (
        PolicyEmbeddingService()
    )

    vector_store = PolicyVectorStore(
        str(VECTOR_STORE_PATH)
    )

    vector_store.load()

    retriever = PolicyRetriever(
        embedding_service=embedding_service,
        vector_store=vector_store,
    )

    return PolicySearchTool(
        retriever=retriever
    )
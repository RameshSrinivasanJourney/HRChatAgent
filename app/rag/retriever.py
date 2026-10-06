from app.rag.embeddings import PolicyEmbeddingService
from app.rag.vector_store import PolicyVectorStore


class PolicyRetriever:

    def __init__(
        self,
        embedding_service: PolicyEmbeddingService,
        vector_store: PolicyVectorStore,
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:

        query_embedding = (
            self.embedding_service.embed_query(query)
        )

        return self.vector_store.search(
            query_embedding,
            top_k=top_k,
        )
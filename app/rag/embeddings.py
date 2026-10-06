from sentence_transformers import SentenceTransformer


class PolicyEmbeddingService:
    """
    Creates semantic embeddings for HR policy text.
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        self.model = SentenceTransformer(model_name)

    def embed_documents(
        self,
        texts: list[str],
    ):
        if not texts:
            raise ValueError(
                "texts cannot be empty"
            )

        return self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

    def embed_query(self, query: str):
        if not query or not query.strip():
            raise ValueError(
                "query cannot be empty"
            )

        return self.model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
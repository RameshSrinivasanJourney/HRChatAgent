from dataclasses import dataclass


@dataclass
class DocumentChunk:
    chunk_id: int
    text: str
    source: str


class PolicyChunker:
    """
    Splits policy documents into overlapping text chunks.
    """

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 120,
    ):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")

        if chunk_overlap < 0:
            raise ValueError(
                "chunk_overlap cannot be negative"
            )

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size"
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(
        self,
        text: str,
        source: str,
    ) -> list[DocumentChunk]:

        text = text.strip()

        if not text:
            return []

        chunks = []

        start = 0
        chunk_id = 0

        while start < len(text):
            end = min(
                start + self.chunk_size,
                len(text),
            )

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        text=chunk_text,
                        source=source,
                    )
                )

                chunk_id += 1

            if end >= len(text):
                break

            start = end - self.chunk_overlap

        return chunks
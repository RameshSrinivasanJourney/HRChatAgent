from pathlib import Path


class PolicyDocumentLoader:
    """
    Loads HR policy documents from the filesystem.
    """

    def load(self, file_path: str) -> str:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Policy document not found: {file_path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Policy path is not a file: {file_path}"
            )

        content = path.read_text(
            encoding="utf-8"
        ).strip()

        if not content:
            raise ValueError(
                f"Policy document is empty: {file_path}"
            )

        return content
from app.rag.loader import PolicyDocumentLoader
from app.rag.chunker import PolicyChunker


def test_policy_loader(tmp_path):

    policy_file = tmp_path / "policy.txt"

    policy_file.write_text(
        "Casual Leave entitlement is 12 days.",
        encoding="utf-8",
    )

    loader = PolicyDocumentLoader()

    result = loader.load(
        str(policy_file)
    )

    assert (
        result
        == "Casual Leave entitlement is 12 days."
    )


def test_policy_loader_missing_file():

    loader = PolicyDocumentLoader()

    try:
        loader.load(
            "does-not-exist.txt"
        )

        assert False

    except FileNotFoundError:
        assert True


def test_policy_loader_empty_file(tmp_path):

    policy_file = tmp_path / "empty.txt"

    policy_file.write_text(
        "",
        encoding="utf-8",
    )

    loader = PolicyDocumentLoader()

    try:
        loader.load(
            str(policy_file)
        )

        assert False

    except ValueError:
        assert True


def test_policy_chunker():

    text = "A" * 2000

    chunker = PolicyChunker(
        chunk_size=500,
        chunk_overlap=50,
    )

    chunks = chunker.split(
        text,
        source="policy.txt",
    )

    assert len(chunks) > 1

    assert chunks[0].source == "policy.txt"

    assert chunks[0].chunk_id == 0


def test_policy_chunker_empty_text():

    chunker = PolicyChunker()

    chunks = chunker.split(
        "",
        source="policy.txt",
    )

    assert chunks == []


def test_policy_chunker_invalid_size():

    try:
        PolicyChunker(
            chunk_size=100,
            chunk_overlap=100,
        )

        assert False

    except ValueError:
        assert True
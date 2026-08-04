from app.search.bm25 import BM25


def test_bm25_score():

    score = BM25.score(
        term_frequency=5,
        document_frequency=10,
        total_documents=100,
        document_length=200,
        average_document_length=150,
    )

    assert score > 0
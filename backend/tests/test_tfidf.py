from app.search.tfidf import TFIDF


def test_term_frequency():

    tokens = [
        "python",
        "python",
        "fastapi",
    ]

    tf = TFIDF.term_frequency(tokens)

    assert round(tf["python"], 2) == 0.67
    assert round(tf["fastapi"], 2) == 0.33


def test_inverse_document_frequency():

    idf = TFIDF.inverse_document_frequency(
        100,
        10,
    )

    assert idf > 1
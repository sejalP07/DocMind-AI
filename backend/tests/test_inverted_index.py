from app.search.inverted_index import InvertedIndex


def test_index():

    idx = InvertedIndex()

    idx.add_document(
        1,
        "Python Search Engine FastAPI"
    )

    idx.add_document(
        2,
        "Python Tutorial"
    )

    idx.add_document(
        3,
        "Docker FastAPI"
    )

    assert idx.search("python") == {1, 2}

    assert idx.search("fastapi") == {1, 3}

    assert idx.search("search") == {1}

    assert idx.search("python search") == {1}
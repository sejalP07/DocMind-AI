from app.search.tokenizer import tokenize
from app.search.stopwords import STOPWORDS


def preprocess(text: str) -> list[str]:
    """
    Tokenize text and remove stopwords.

    Example:
        Input:
            "This is the Python Search Engine"

        Output:
            ["python", "search", "engine"]
    """

    tokens = tokenize(text)

    filtered = [
        token
        for token in tokens
        if token not in STOPWORDS
    ]

    return filtered
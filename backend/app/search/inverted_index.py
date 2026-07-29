from collections import defaultdict
from typing import Dict, Set

from app.search.preprocess import preprocess


class InvertedIndex:
    """
    Simple in-memory inverted index.

    word -> {document ids}
    """

    def __init__(self):
        self.index: Dict[str, Set[int]] = defaultdict(set)

    def add_document(self, document_id: int, text: str):

        tokens = preprocess(text)

        for token in tokens:
            self.index[token].add(document_id)

    def remove_document(self, document_id: int):

        for token in list(self.index.keys()):

            self.index[token].discard(document_id)

            if not self.index[token]:
                del self.index[token]

    def search(self, query: str):

        tokens = preprocess(query)

        if not tokens:
            return set()

        results = None

        for token in tokens:

            docs = self.index.get(token, set())

            if results is None:
                results = docs.copy()
            else:
                results &= docs

        return results or set()
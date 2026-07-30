from collections import Counter, defaultdict
from typing import Dict, Set

from app.search.preprocess import preprocess


class InvertedIndex:
    """
    Simple in-memory inverted index.

    word -> {document ids}
    """

    def __init__(self):
        # term -> {document_id: term_frequency}
        self.index: Dict[str, Dict[int, int]] = defaultdict(dict)

        # Total indexed documents
        self.total_documents = 0

        # document_id -> total number of terms
        self.document_lengths: Dict[int, int] = {}

        # term -> number of documents containing the term
        self.document_frequency: Dict[str, int] = defaultdict(int)

    def add_document(self, document_id: int, text: str):
        tokens = preprocess(text)

        if not tokens:
            return

        self.total_documents += 1
        self.document_lengths[document_id] = len(tokens)

        term_counts = Counter(tokens)

        for term, frequency in term_counts.items():
            self.index[term][document_id] = frequency
            self.document_frequency[term] += 1

    def remove_document(self, document_id: int):
        if document_id in self.document_lengths:
            del self.document_lengths[document_id]
            self.total_documents -= 1

        for term in list(self.index.keys()):
            if document_id in self.index[term]:
                del self.index[term][document_id]
                self.document_frequency[term] -= 1

                if not self.index[term]:
                    del self.index[term]
                    del self.document_frequency[term]

    def search(self, query: str):
        tokens = preprocess(query)

        if not tokens:
            return set()

        results = None

        for token in tokens:
            docs = set(self.index.get(token, {}).keys())

            if results is None:
                results = docs.copy()
            else:
                results &= docs

        return results or set()
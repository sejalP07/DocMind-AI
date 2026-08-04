from collections import defaultdict
from typing import Dict

from app.search.preprocess import preprocess


class InvertedIndex:
    """
    In-memory inverted index.

    Structure:
        word -> {document_id: term_frequency}
    """

    def __init__(self):

        # token -> {doc_id: frequency}
        self.index: Dict[str, Dict[int, int]] = defaultdict(dict)

        # token -> number of documents containing token
        self.document_frequency: Dict[str, int] = defaultdict(int)

        # doc_id -> document length
        self.document_lengths: Dict[int, int] = {}

        # total indexed documents
        self.total_documents = 0

    def add_document(
        self,
        document_id: int,
        text: str,
    ):

        tokens = preprocess(text)

        self.document_lengths[document_id] = len(tokens)

        self.total_documents += 1

        frequencies = defaultdict(int)

        for token in tokens:
            frequencies[token] += 1

        for token, frequency in frequencies.items():

            self.index[token][document_id] = frequency

            self.document_frequency[token] += 1

    def remove_document(
        self,
        document_id: int,
    ):

        for token in list(self.index.keys()):

            if document_id in self.index[token]:

                del self.index[token][document_id]

                self.document_frequency[token] -= 1

                if self.document_frequency[token] == 0:
                    del self.document_frequency[token]
                    del self.index[token]

        if document_id in self.document_lengths:
            del self.document_lengths[document_id]

        self.total_documents -= 1

    def search(
        self,
        query: str,
    ):

        tokens = preprocess(query)

        if not tokens:
            return set()

        results = None

        for token in tokens:

            docs = set(self.index.get(token, {}).keys())

            if results is None:
                results = docs
            else:
                results &= docs

        return results or set()
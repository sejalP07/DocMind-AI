import math
from collections import Counter


class TFIDF:

    @staticmethod
    def term_frequency(tokens):
        """
        Returns normalized term frequencies.
        """
        counts = Counter(tokens)
        total = len(tokens)

        return {
            word: freq / total
            for word, freq in counts.items()
        }

    @staticmethod
    def inverse_document_frequency(
        total_documents,
        document_frequency,
    ):
        """
        Computes IDF with smoothing.
        """
        return math.log(
            (total_documents + 1)
            / (document_frequency + 1)
        ) + 1

    @staticmethod
    def score(
        tf,
        idf,
    ):
        return tf * idf
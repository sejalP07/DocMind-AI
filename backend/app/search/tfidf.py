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

    @staticmethod
    def rank_documents(
        query_tokens,
        index,
        total_documents,
        document_frequency,
    ):
        """
        Calculate TF-IDF scores for matching documents.
        """

        scores = {}

        for term in query_tokens:

            if term not in index:
                continue

            idf = TFIDF.inverse_document_frequency(
                total_documents,
                document_frequency[term],
            )

            for document_id, frequency in index[term].items():

                tf = frequency

                scores[document_id] = (
                    scores.get(document_id, 0)
                    + TFIDF.score(tf, idf)
                )

        return sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )
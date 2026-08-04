import math


class BM25:

    k1 = 1.5
    b = 0.75

    @staticmethod
    def score(
        term_frequency: int,
        document_frequency: int,
        total_documents: int,
        document_length: int,
        average_document_length: float,
    ):

        idf = math.log(
            (
                total_documents
                - document_frequency
                + 0.5
            )
            /
            (
                document_frequency
                + 0.5
            )
            + 1
        )

        numerator = term_frequency * (BM25.k1 + 1)

        denominator = (
            term_frequency
            + BM25.k1
            * (
                1
                - BM25.b
                + BM25.b
                * (
                    document_length
                    / average_document_length
                )
            )
        )

        return idf * (numerator / denominator)
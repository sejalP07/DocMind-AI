from difflib import get_close_matches


class FuzzySearch:

    @staticmethod
    def correct_query(index, query: str):
        """
        Correct misspelled query terms using the indexed vocabulary.
        """

        words = query.lower().split()

        corrected = []

        vocabulary = list(index.index.keys())

        for word in words:

            if word in vocabulary:
                corrected.append(word)
                continue

            matches = get_close_matches(
                word,
                vocabulary,
                n=1,
                cutoff=0.7,
            )

            if matches:
                corrected.append(matches[0])
            else:
                corrected.append(word)

        return " ".join(corrected)
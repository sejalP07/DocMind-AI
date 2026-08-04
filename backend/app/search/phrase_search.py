from app.search.preprocess import preprocess


class PhraseSearch:

    @staticmethod
    def search(
        documents,
        phrase: str,
    ):
        """
        Returns only documents containing the exact phrase.
        """

        phrase_tokens = preprocess(phrase)

        if not phrase_tokens:
            return []

        normalized_phrase = " ".join(phrase_tokens)

        results = []

        for document in documents:

            normalized_content = " ".join(
                preprocess(document.content)
            )

            if normalized_phrase in normalized_content:
                results.append(document)

        return results
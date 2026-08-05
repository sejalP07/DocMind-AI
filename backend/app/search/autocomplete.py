class Autocomplete:

    @staticmethod
    def suggest(
        index,
        prefix: str,
        limit: int = 10,
    ):
        """
        Returns words beginning with the given prefix.
        """

        prefix = prefix.lower()

        suggestions = []

        for word in sorted(index.index.keys()):

            if word.startswith(prefix):
                suggestions.append(word)

            if len(suggestions) >= limit:
                break

        return suggestions
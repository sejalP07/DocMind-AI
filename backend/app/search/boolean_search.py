from app.search.preprocess import preprocess


class BooleanSearch:

    @staticmethod
    def search(index, query: str):

        query = query.strip()

        # AND
        if " AND " in query:
            left, right = query.split(" AND ")

            left_docs = set(index.search(left))
            right_docs = set(index.search(right))

            return left_docs & right_docs

        # OR
        if " OR " in query:
            left, right = query.split(" OR ")

            left_docs = set(index.search(left))
            right_docs = set(index.search(right))

            return left_docs | right_docs

        # NOT
        if " NOT " in query:
            left, right = query.split(" NOT ")

            left_docs = set(index.search(left))
            right_docs = set(index.search(right))

            return left_docs - right_docs

        return index.search(query)
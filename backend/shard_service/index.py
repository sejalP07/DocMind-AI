from app.search.inverted_index import InvertedIndex


class ShardIndex:

    def __init__(self):
        self.index = InvertedIndex()

    def build(self, documents):

        for document in documents:

            self.index.add_document(
                document["id"],
                document["content"],
            )

    def search(self, query):

        return self.index.search(query)
from app.search.sharding import Sharding


class Document:

    def __init__(self, doc_id):
        self.id = doc_id


documents = [
    Document(1),
    Document(2),
    Document(3),
    Document(4),
    Document(5),
    Document(6),
]

shards = Sharding.partition_documents(
    documents,
    3,
)

for i, shard in enumerate(shards):
    print(
        f"Shard {i}:",
        [doc.id for doc in shard],
    )
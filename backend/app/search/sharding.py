from typing import List


class Sharding:

    @staticmethod
    def get_shard(document_id: int, total_shards: int) -> int:
        """
        Returns the shard number for a document.
        """
        return document_id % total_shards

    @staticmethod
    def partition_documents(
        documents,
        total_shards: int,
    ):
        """
        Split documents across shards.
        """

        shards: List[list] = [
            [] for _ in range(total_shards)
        ]

        for document in documents:

            shard = Sharding.get_shard(
                document.id,
                total_shards,
            )

            shards[shard].append(document)

        return shards
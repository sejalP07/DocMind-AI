class ShardRouter:

    @staticmethod
    def get_shard(document_id: int) -> str:

        remainder = document_id % 3

        if remainder == 1:
            return "http://shard1:8001"

        if remainder == 2:
            return "http://shard2:8002"

        return "http://shard3:8003"
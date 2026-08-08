class ShardRouter:

    @staticmethod
    def get_shard(document_id: int) -> str:

        remainder = document_id % 3

        if remainder == 1:
            return "http://127.0.0.1:8001"

        if remainder == 2:
            return "http://127.0.0.1:8002"

        return "http://127.0.0.1:8003"
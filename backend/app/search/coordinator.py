import asyncio
import httpx
import json
from app.core.redis import redis_client
import time

class SearchCoordinator:

    SHARDS = {
        1: "http://shard1:8001",
        2: "http://shard2:8002",
        3: "http://shard3:8003",
    }
    cache_hits = 0
    cache_misses = 0

    async def get_shard_stats(
        self,
        client: httpx.AsyncClient,
        shard_id: int,
        url: str,
    ):
        try:
            response = await client.get(
                f"{url}/stats",
                timeout=3.0,
            )

            response.raise_for_status()

            return response.json()

        except Exception as exc:
            print(
                f"Stats failed for shard {shard_id}: {exc}"
            )

            return None

    async def search_shard(
        self,
        client: httpx.AsyncClient,
        shard_id: int,
        url: str,
        query: str,
        global_stats: dict,
    ):
        params = {
            "q": query,
            "total_documents": global_stats["total_documents"],
            "average_document_length": global_stats[
                "average_document_length"
            ],
            "document_frequency": json.dumps(
                global_stats["document_frequency"]
            ),
        }

        start_time = time.perf_counter()

        for attempt in range(2):

            try:
                response = await client.get(
                    f"{url}/search",
                    params=params,
                    timeout=3.0,
                )

                response.raise_for_status()

                latency_ms = (
                    time.perf_counter() - start_time
                ) * 1000

                return {
                    "shard": shard_id,
                    "status": "success",
                    "latency_ms": round(latency_ms, 2),
                    "results": response.json(),
                }

            except Exception as exc:

                print(
                    f"Shard {shard_id} "
                    f"attempt {attempt + 1} failed: {exc}"
                )

                if attempt == 1:
                    latency_ms = (
                        time.perf_counter() - start_time
                    ) * 1000

                    return {
                        "shard": shard_id,
                        "status": "failed",
                        "latency_ms": round(
                            latency_ms,
                            2,
                        ),
                        "results": [],
                    }

                await asyncio.sleep(0.2)

    async def check_shard_health(
        self,
        client: httpx.AsyncClient,
        shard_id: int,
        url: str,
    ):
        try:
            response = await client.get(
                f"{url}/health",
                timeout=1.0,
            )

            response.raise_for_status()

            return {
                "shard": shard_id,
                "healthy": True,
            }

        except Exception as exc:
            print(
                f"Shard {shard_id} unhealthy: {exc}"
            )

            return {
                "shard": shard_id,
                "healthy": False,
            }

    async def get_healthy_shards(self):

        async with httpx.AsyncClient() as client:
            tasks = [
                self.check_shard_health(
                    client,
                    shard_id,
                    url,
                )
                for shard_id, url in self.SHARDS.items()
            ]

            health_results = await asyncio.gather(*tasks)

        return {
            result["shard"]
            for result in health_results
            if result["healthy"]
        }

    async def search(self, query: str):
        search_start = time.perf_counter()

        query = query.strip().lower()
        cache_key = f"distributed-search:{query}"

        # -----------------------------
        # CACHE HIT
        # -----------------------------
        cached = redis_client.get(cache_key)

        if cached:
            self.cache_hits += 1

            print(
                f"Distributed Search Cache HIT "
                f"(hits={self.cache_hits})"
            )

            response = json.loads(cached)

            # Dynamic metrics are added AFTER
            # reading the cached search result.
            response["cache_hit"] = True
            response["cache_hits"] = self.cache_hits
            response["cache_misses"] = self.cache_misses

            return response

        # -----------------------------
        # CACHE MISS
        # -----------------------------
        self.cache_misses += 1

        print(
            f"Distributed Search Cache MISS "
            f"(misses={self.cache_misses})"
        )

        healthy_shards = await self.get_healthy_shards()

        failed_shards = [
            shard_id
            for shard_id in self.SHARDS
            if shard_id not in healthy_shards
        ]

        # -----------------------------
        # GLOBAL BM25 STATISTICS
        # -----------------------------
        global_stats = await self.get_global_stats()

        # -----------------------------
        # SEARCH HEALTHY SHARDS
        # -----------------------------
        async with httpx.AsyncClient() as client:

            tasks = [
                self.search_shard(
                    client,
                    shard_id,
                    self.SHARDS[shard_id],
                    query,
                    global_stats,
                )
                for shard_id in healthy_shards
            ]

            shard_results = await asyncio.gather(*tasks)

        results = []
        shard_latency = {}

        for shard_result in shard_results:

            shard_latency[
                str(shard_result["shard"])
            ] = shard_result["latency_ms"]

            if shard_result["status"] == "failed":
                failed_shards.append(
                    shard_result["shard"]
                )
                continue

            for result in shard_result["results"]:
                result["shard"] = shard_result["shard"]
                results.append(result)

        # -----------------------------
        # GLOBAL RANKING
        # -----------------------------
        results.sort(
            key=lambda x: x.get("score", 0),
            reverse=True,
        )

        total_latency_ms = (
            time.perf_counter() - search_start
        ) * 1000

        # -----------------------------
        # STABLE SEARCH RESPONSE
        # -----------------------------
        cached_response = {
            "query": query,
            "total": len(results),
            "partial": len(failed_shards) > 0,
            "failed_shards": failed_shards,
            "shard_latency_ms": shard_latency,
            "total_latency_ms": round(
                total_latency_ms,
                2,
            ),
            "results": results,
        }

        # -----------------------------
        # SAVE ONLY STABLE DATA
        # -----------------------------
        redis_client.set(
            cache_key,
            json.dumps(cached_response),
            ex=300,
        )

        print("Distributed Search Cache SAVED")

        # -----------------------------
        # RETURN WITH DYNAMIC METRICS
        # -----------------------------
        response = cached_response.copy()

        response["cache_hit"] = False
        response["cache_hits"] = self.cache_hits
        response["cache_misses"] = self.cache_misses

        return response
    
    def invalidate_cache(self):
        try:
            keys = redis_client.keys(
                "distributed-search:*"
            )

            if keys:
                redis_client.delete(*keys)

            print(
                f"Invalidated {len(keys)} distributed search cache entries"
            )

        except Exception as exc:
            print(f"Cache invalidation failed: {exc}")
        
    async def get_global_stats(self):

        async with httpx.AsyncClient() as client:

            tasks = [
                self.get_shard_stats(
                    client,
                    shard_id,
                    url,
                )
                for shard_id, url in self.SHARDS.items()
            ]

            shard_stats = await asyncio.gather(
                *tasks
            )

        total_documents = 0
        total_length = 0
        document_frequency = {}

        for stats in shard_stats:

            if stats is None:
                continue

            total_documents += stats["total_documents"]
            total_length += stats["total_length"]

            for term, frequency in stats[
                "document_frequency"
            ].items():

                document_frequency[term] = (
                    document_frequency.get(term, 0)
                    + frequency
                )

        average_document_length = (
            total_length / total_documents
            if total_documents
            else 0
        )

        return {
            "total_documents": total_documents,
            "total_length": total_length,
            "average_document_length": average_document_length,
            "document_frequency": document_frequency,
        }
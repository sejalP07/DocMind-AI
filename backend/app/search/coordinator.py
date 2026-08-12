import asyncio
import httpx
import json
import logging
import os
import time

from app.core.redis import redis_client



logger = logging.getLogger(__name__)

class SearchCoordinator:

    SHARDS = {
        1: os.getenv("SHARD_1_URL", "http://shard1:8001"),
        2: os.getenv("SHARD_2_URL", "http://shard2:8002"),
        3: os.getenv("SHARD_3_URL", "http://shard3:8003"),
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
                timeout=5.0,
            )

            response.raise_for_status()

            return response.json()

        except Exception as exc:
            logger.warning(
                "shard_stats_failed",
                extra={
                    "shard_id": shard_id,
                    "error": str(exc),
                },
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
                    timeout=5.0,
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

                logger.warning(
                    "shard_search_failed",
                    extra={
                        "shard_id": shard_id,
                        "attempt": attempt + 1,
                        "error": str(exc),
                    },
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
                timeout=5.0,
            )

            response.raise_for_status()

            logger.info(
                "shard_healthy",
                extra={
                    "shard_id": shard_id,
                    "status_code": response.status_code,
                },
            )

            return {
                "shard": shard_id,
                "healthy": True,
            }

        except Exception as exc:
            logger.warning(
                "shard_unhealthy",
                extra={
                    "shard_id": shard_id,
                    "error": str(exc),
                },
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

    async def search(
        self,
        query: str,
        page: int = 1,
        page_size: int = 10,
    ):
        search_start = time.perf_counter()

        query = query.strip().lower()
        page = max(page, 1)
        page_size = max(min(page_size, 100), 1)
        cache_key = (
            f"distributed-search:{query}"
            f":page:{page}"
            f":page_size:{page_size}"
        )

        # -----------------------------
        # CACHE HIT
        # -----------------------------
        cached = redis_client.get(cache_key)

        if cached:
            self.cache_hits += 1

            logger.info(
                "distributed_search_cache_hit",
                extra={
                    "query": query,
                    "cache_hits": self.cache_hits,
                },
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

        logger.info(
            "distributed_search_cache_miss",
            extra={
                "query": query,
                "cache_misses": self.cache_misses,
            },
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
        total_results = len(results)

        total_pages = (
            (total_results + page_size - 1) // page_size
            if total_results
            else 0
        )

        start = (page - 1) * page_size
        end = start + page_size

        paginated_results = results[start:end]

        total_latency_ms = (
            time.perf_counter() - search_start
        ) * 1000

        # -----------------------------
        # STABLE SEARCH RESPONSE
        # -----------------------------
        cached_response = {
            "query": query,
            "total": total_results,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "partial": len(failed_shards) > 0,
            "failed_shards": failed_shards,
            "shard_latency_ms": shard_latency,
            "total_latency_ms": round(
                total_latency_ms,
                2,
            ),
            "results": paginated_results,
        }

        # -----------------------------
        # SAVE ONLY STABLE DATA
        # -----------------------------
        if not failed_shards:
            redis_client.set(
                cache_key,
                json.dumps(cached_response),
                ex=300,
            )

            logger.info(
                "distributed_search_cache_saved",
                extra={
                    "query": query,
                    "page": page,
                    "page_size": page_size,
                },
            )
        else:
            logger.warning(
                "distributed_search_cache_skipped",
                extra={
                    "query": query,
                    "failed_shards": failed_shards,
                },
            )
        # -----------------------------
        # RETURN WITH DYNAMIC METRICS
        # -----------------------------
        response = cached_response.copy()

        response["cache_hit"] = False
        response["cache_hits"] = self.cache_hits
        response["cache_misses"] = self.cache_misses

        logger.info(
            "distributed_search_completed",
            extra={
                "query": query,
                "total_results": total_results,
                "page": page,
                "page_size": page_size,
                "failed_shards": failed_shards,
                "total_latency_ms": round(
                    total_latency_ms,
                    2,
                ),
            },
        )

        return response
    
    def invalidate_cache(self):
        try:
            keys = redis_client.keys(
                "distributed-search:*"
            )

            if keys:
                redis_client.delete(*keys)

            logger.info(
                "distributed_search_cache_invalidated",
                extra={
                    "invalidated_keys": len(keys),
                },
            )

        except Exception as exc:
            logger.warning(
                "cache_invalidation_failed",
                extra={
                    "error": str(exc),
                },
            )
        
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
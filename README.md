# DocMind-AI | Distributed Search Engine

A distributed search engine built with **Python, FastAPI, PostgreSQL, Redis, and Docker**, designed to retrieve, rank, and aggregate search results across multiple independent shards.\


## Overview

DocMind-AI implements a distributed search architecture in which a central coordinator sends search queries to multiple independent shard services, collects their responses, and combines them into a globally ranked result set.

The system uses **BM25 relevance scoring** to rank documents, **Redis** to cache repeated search queries, and **PostgreSQL** for persistent storage. It also incorporates concurrent shard requests, health monitoring, pagination, and partial-result handling to improve search performance and resilience.

## Features

- **Distributed Search:** Execute queries across three independent search shards.
- **Global BM25 Ranking:** Aggregate shard results and rank documents using global search statistics.
- **Concurrent Query Execution:** Query available shards asynchronously.
- **Redis Caching:** Cache search responses with a five-minute TTL to reduce repeated processing.
- **Fault Tolerance:** Return partial results when individual shards become unavailable.
- **Document Management:** Create, retrieve, list, and delete documents through REST APIs.
- **Pagination:** Retrieve ranked results in manageable pages.
- **Health Monitoring:** Check API and shard availability.
- **Performance Metrics:** Track shard latency, cache hits, cache misses, and search execution.
- **Containerized Deployment:** Run the application and supporting services using Docker Compose.
- **Automated Testing:** Validate search logic, API behavior, caching, and distributed-service functionality.

## Architecture

```text
                  Client / Frontend
                         |
                         v
                FastAPI Coordinator
                         |
                   Redis Cache
                         |
              +----------+----------+
              |          |          |
              v          v          v
           Shard 1     Shard 2     Shard 3
              |          |          |
              +----------+----------+
                         |
                 Result Aggregation
                         |
                  Global BM25 Rank
                         |
                    Pagination
                         |
                         v
                  Search Response

          PostgreSQL: Persistent Storage
          Docker Compose: Service Orchestration
```

## Technology Stack

| Technology     | Purpose                       |
| -------------- | ----------------------------- |
| Python         | Core search and backend logic |
| FastAPI        | REST API development          |
| PostgreSQL     | Persistent document storage   |
| SQLAlchemy     | Database interaction          |
| Redis          | Search-result caching         |
| HTTPX          | Asynchronous HTTP requests    |
| BM25           | Document relevance ranking    |
| Docker         | Containerization              |
| Docker Compose | Multi-service orchestration   |
| Pytest         | Automated testing             |

## How It Works

1. A client submits a search query to the FastAPI coordinator.
2. The coordinator checks Redis for a cached response.
3. On a cache miss, the coordinator checks shard availability.
4. The query is sent concurrently to healthy shards.
5. Each shard retrieves and scores matching documents.
6. The coordinator aggregates results and applies global BM25 ranking.
7. Pagination is applied to the ranked results.
8. The response is cached in Redis and returned to the client.
9. If a shard fails, available results can still be returned with failure information.

## Getting Started

### Prerequisites

- Git
- Docker Desktop
- Docker Compose

### 1. Clone the repository

```bash
git clone https://github.com/sejalP07/DocMind-AI.git
cd DocMind-AI
```

### 2. Start the application

```bash
docker compose up -d --build
```

### 3. Check running services

```bash
docker compose ps
```

### 4. Access the API documentation

Open the following URL after the application starts:

**Swagger UI:** [http://localhost:8005/docs](http://localhost:8005/docs)

**ReDoc:** [http://localhost:8005/redoc](http://localhost:8005/redoc)

### 5. View application logs

```bash
docker compose logs -f
```

### 6. Stop the application

```bash
docker compose down
```

## API Endpoints

| Method | Endpoint              | Description                  |
| ------ | --------------------- | ---------------------------- |
| POST   | `/documents`          | Create a document            |
| GET    | `/documents`          | List documents               |
| GET    | `/documents/{id}`     | Retrieve a document          |
| DELETE | `/documents/{id}`     | Delete a document            |
| GET    | `/search`             | Search documents             |
| GET    | `/distributed-search` | Search across shards         |
| GET    | `/autocomplete`       | Retrieve search suggestions  |
| GET    | `/health`             | Check application health     |
| GET    | `/metrics`            | Retrieve application metrics |

### Example: Distributed Search

```bash
curl "http://localhost:8005/distributed-search?q=python&page=1&page_size=10"
```

### Example: Health Check

```bash
curl http://localhost:8005/health
```

Refer to `/docs` for the complete API schemas and supported parameters.

## Fault Tolerance and Caching

**Fault tolerance:** The coordinator checks shard health and can return partial search results when one or more shards are unavailable, along with information identifying failed shards.

**Caching:** Redis stores eligible search responses for five minutes. Cache invalidation helps prevent stale search results after document modifications.

**Observability:** Shard latency, cache statistics, and application logs help identify bottlenecks and troubleshoot failures.

## Testing

Run the project's test suite inside the API container:

```bash
docker exec distributed-search-api python -m pytest /app/tests -v
```

Tests cover search ranking, database connectivity, API endpoints, Redis caching, performance metrics, and shard failure handling.

## Project Structure

```text
DocMind-AI/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── database/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── search/
│   │   └── services/
│   ├── shard_service/
│   ├── shard_service2/
│   ├── shard_service3/
│   └── tests/
├── frontend/
├── docs/
├── docker-compose.yml
├── docker-compose.local.yml
└── README.md
```

## Future Enhancements

- Hybrid keyword and semantic search.
- Embedding-based document retrieval.
- LLM-powered result reranking.
- Dynamic shard rebalancing.
- Distributed tracing and advanced monitoring.
- Load testing and performance benchmarking.
- Kubernetes deployment.

## Learning Outcomes

This project demonstrates practical implementation of distributed query processing, search information retrieval, asynchronous backend communication, caching strategies, fault tolerance, database integration, and containerized infrastructure.

## Author

**Sejal P.**

GitHub: [@sejalP07](https://github.com/sejalP07)

Repository: [DocMind-AI](https://github.com/sejalP07/DocMind-AI)

---

If you find this project useful, consider giving the repository a ⭐.

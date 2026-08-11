# Distributed Search Engine

A production-style **distributed search backend** built with FastAPI, PostgreSQL, Redis, Docker, and multiple independent shard services.

The system distributes search queries across three shards, performs BM25-based ranking, aggregates results globally, supports pagination and partial-result handling, and uses Redis to cache stable search responses.

---

## 🚀 Key Features

* Distributed search across **3 independent shard services**
* Parallel shard querying using asynchronous HTTP requests
* Global **BM25 ranking**
* Global document statistics for consistent scoring
* Redis-based search-result caching
* Cache hit/miss metrics
* Cache invalidation after document changes
* Pagination support
* Shard health checks
* Partial-result handling when a shard fails
* Shard recovery handling
* RESTful document CRUD APIs
* Autocomplete API
* Request validation using FastAPI
* Structured application logging
* PostgreSQL persistence
* Dockerized deployment
* Docker healthchecks and dependency ordering
* Automated unit and integration tests
* Search performance testing
* API metrics endpoint

---

## 🏗️ Architecture

```text
                         ┌──────────────────────┐
                         │      Client / UI     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      FastAPI API     │
                         │                      │
                         │  REST API +          │
                         │  Search Coordinator  │
                         └──────────┬───────────┘
                                    │
                     ┌──────────────┼──────────────┐
                     │              │              │
                     ▼              ▼              ▼
              ┌────────────┐ ┌────────────┐ ┌────────────┐
              │   Shard 1  │ │   Shard 2  │ │   Shard 3  │
              │   FastAPI  │ │   FastAPI  │ │   FastAPI  │
              │    BM25    │ │    BM25    │ │    BM25    │
              └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
                    │              │              │
                    └──────────────┼──────────────┘
                                   │
                                   ▼
                         ┌──────────────────────┐
                         │  Global Aggregation  │
                         │                      │
                         │  • Merge results     │
                         │  • Global ranking    │
                         │  • Pagination        │
                         │  • Failure handling  │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │        Redis         │
                         │                      │
                         │ Search Result Cache  │
                         └──────────────────────┘

                         ┌──────────────────────┐
                         │     PostgreSQL       │
                         │                      │
                         │ Persistent Documents │
                         └──────────────────────┘
```

---

## 🔄 Search Request Flow

1. Client sends a search request to the FastAPI API.
2. The API validates query parameters.
3. The search coordinator checks Redis for a cached response.
4. On a cache miss, the coordinator retrieves global document statistics.
5. The coordinator checks shard health.
6. The query is sent to healthy shards concurrently.
7. Each shard performs BM25-based search.
8. Shard results are returned to the coordinator.
9. The coordinator merges results from all available shards.
10. Results are globally sorted by BM25 score.
11. Pagination is applied.
12. The stable search response is stored in Redis.
13. The response is returned to the client.

---

## 🛡️ Distributed Failure Handling

The coordinator is designed to tolerate individual shard failures.

For example, if Shard 2 becomes unavailable:

```json
{
  "partial": true,
  "failed_shards": [2]
}
```

The remaining healthy shards can still return search results.

After Shard 2 recovers:

```json
{
  "partial": false,
  "failed_shards": []
}
```

Shard failure and recovery are covered by automated integration tests.

---

## ⚡ Caching

Redis is used to cache stable distributed-search responses.

Example cache flow:

```text
Search Request
      │
      ▼
   Redis?
   /    \
 HIT    MISS
 │        │
 ▼        ▼
Return   Query Shards
Cache       │
            ▼
       Rank Results
            │
            ▼
        Save Redis
            │
            ▼
        Return Result
```

Cached search responses have a **5-minute TTL**.

The API exposes cache metrics including:

* `cache_hit`
* `cache_hits`
* `cache_misses`

Example:

```json
{
  "cache_hit": true,
  "cache_hits": 3,
  "cache_misses": 1
}
```

---

## 📊 Example Distributed Search

Request:

```text
GET /distributed-search?q=python&page=1&page_size=10
```

Example:

```json
{
  "query": "python",
  "total": 4,
  "page": 1,
  "page_size": 10,
  "total_pages": 1,
  "partial": false,
  "failed_shards": [],
  "shard_latency_ms": {
    "1": 32.06,
    "2": 28.95,
    "3": 27.78
  },
  "total_latency_ms": 563.78,
  "results": [
    {
      "id": 2,
      "title": "Advanced Python",
      "score": 1.1895,
      "shard": 2
    },
    {
      "id": 1,
      "title": "Python FastAPI Guide",
      "score": 0.9838,
      "shard": 1
    },
    {
      "id": 3,
      "title": "Python Basics",
      "score": 0.7901,
      "shard": 3
    },
    {
      "id": 6,
      "title": "Docker Search Test",
      "score": 0.7027,
      "shard": 3
    }
  ],
  "cache_hit": false
}
```

---

## 🧮 Search Ranking

The search engine uses **BM25-based ranking**.

The distributed architecture retrieves results independently from each shard and then performs global ranking at the coordinator.

```text
Shard 1 Results ─┐
                 │
Shard 2 Results ─┼──► Coordinator ──► Global Ranking
                 │
Shard 3 Results ─┘
                         │
                         ▼
                    Pagination
                         │
                         ▼
                     Response
```

Global document statistics are used to maintain consistent ranking across shards.

---

## 🧰 Tech Stack

| Technology     | Purpose                                            |
| -------------- | -------------------------------------------------- |
| Python 3.10    | Backend development                                |
| FastAPI        | REST APIs and shard services                       |
| PostgreSQL     | Persistent document storage                        |
| Redis          | Search-result caching                              |
| HTTPX          | Async communication between coordinator and shards |
| BM25           | Search ranking                                     |
| Docker         | Containerization                                   |
| Docker Compose | Multi-service orchestration                        |
| Pytest         | Automated testing                                  |
| SQLAlchemy     | Database access                                    |
| Uvicorn        | ASGI server                                        |

---

## 📁 Project Structure

```text
distributed-search-engine/
│
├── backend/
│   │
│   ├── app/
│   │   ├── api/
│   │   │   └── document.py
│   │   │
│   │   ├── core/
│   │   │   └── redis.py
│   │   │
│   │   ├── database/
│   │   │
│   │   ├── repositories/
│   │   │
│   │   ├── schemas/
│   │   │
│   │   ├── search/
│   │   │   ├── bm25.py
│   │   │   ├── coordinator.py
│   │   │   ├── inverted_index.py
│   │   │   ├── phrase_search.py
│   │   │   ├── boolean_search.py
│   │   │   ├── fuzzy_search.py
│   │   │   └── autocomplete.py
│   │   │
│   │   └── services/
│   │       ├── document_service.py
│   │       └── search_service.py
│   │
│   ├── shard_service/
│   ├── shard_service2/
│   ├── shard_service3/
│   │
│   ├── tests/
│   │   ├── integration/
│   │   │   ├── test_cache.py
│   │   │   ├── test_cache_invalidation.py
│   │   │   ├── test_cache_metrics.py
│   │   │   ├── test_health.py
│   │   │   ├── test_metrics.py
│   │   │   ├── test_performance.py
│   │   │   ├── test_search.py
│   │   │   ├── test_shard_failure.py
│   │   │   └── test_shard_recovery.py
│   │   │
│   │   ├── test_bm25.py
│   │   ├── test_connection.py
│   │   ├── test_db.py
│   │   ├── test_inverted_index.py
│   │   └── test_tfidf.py
│   │
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .dockerignore
│
├── docs/
│   └── screenshots/
│       ├── 01-swagger-api.png
│       ├── 02-distributed-search.png
│       ├── 03-docker-services.png
│       ├── 04-test-suite.png
│       └── 05-metrics.png
│
├── frontend/
│
├── docker-compose.yml
└── README.md
```

---

## 🐳 Docker Architecture

The application consists of six services:

```text
                    Docker Compose
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
       ▼                 ▼                 ▼
    FastAPI            Redis           PostgreSQL
      API
       │
       ├──────────────┬──────────────┐
       ▼              ▼              ▼
    Shard 1        Shard 2        Shard 3
```

### Services

| Service    | Internal Port | Host Port |
| ---------- | ------------: | --------: |
| API        |          8000 |      8005 |
| Shard 1    |          8001 |      8001 |
| Shard 2    |          8002 |      8002 |
| Shard 3    |          8003 |      8003 |
| PostgreSQL |          5432 |      5434 |
| Redis      |          6379 |      6379 |

The API uses host port **8005** to avoid conflicts with local development servers using port 8000.

---

## 🏥 Healthchecks

Docker Compose includes healthchecks for:

* PostgreSQL
* Redis
* API
* Shard 1
* Shard 2
* Shard 3

Example:

```yaml
healthcheck:
  test:
    - CMD
    - python
    - -c
    - import urllib.request; urllib.request.urlopen("http://localhost:8000/health")
  interval: 5s
  timeout: 3s
  retries: 10
```

Services use `depends_on` with health conditions so that dependent services start only after their dependencies become healthy.

---

## 🚀 Getting Started

### Prerequisites

Install:

* Docker Desktop
* Docker Compose
* Git

---

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd distributed-search-engine
```

---

### 2. Build and start the system

```bash
docker compose up -d --build
```

---

### 3. Check service status

```bash
docker compose ps
```

All services should be running.

The API should appear similar to:

```text
distributed-search-api     Up
distributed-search-postgres Up (healthy)
distributed-search-redis   Up (healthy)
distributed-search-shard1  Up
distributed-search-shard2  Up
distributed-search-shard3  Up
```

---

## 🔍 API Usage

### API Root

```bash
curl http://127.0.0.1:8005/
```

---

### API Health

```bash
curl http://127.0.0.1:8005/health
```

---

### Distributed Search

```bash
curl "http://127.0.0.1:8005/distributed-search?q=python&page=1&page_size=10"
```

---

### Local Search

```bash
curl "http://127.0.0.1:8005/search?q=python&page=1&size=10"
```

---

### Autocomplete

```bash
curl "http://127.0.0.1:8005/autocomplete?q=p"
```

---

### API Documentation

FastAPI automatically provides Swagger documentation:

```text
http://127.0.0.1:8005/docs
```

ReDoc:

```text
http://127.0.0.1:8005/redoc
```

---

## 🔐 API Validation

Request validation is implemented using FastAPI query constraints.

### Search query

```text
1 <= q length <= 200
```

### Page

```text
page >= 1
```

### Page size

```text
1 <= page_size <= 100
```

Invalid requests return:

```text
422 Unprocessable Entity
```

Example:

```text
/distributed-search?q=python&page=0&page_size=10
```

returns a validation error because `page` must be at least `1`.

---

## 🧪 Automated Testing

The project includes unit and integration tests covering the main distributed-search functionality.

### Run the complete test suite

```bash
docker exec distributed-search-api python -m pytest /app/tests -v
```

Current verified result:

```text
============================== 15 passed in 1.23s ==============================
```

### Test categories

The test suite validates:

* BM25 scoring
* TF-IDF calculations
* inverted index
* PostgreSQL connectivity
* database connectivity
* API health
* distributed search
* Redis caching
* cache invalidation
* cache metrics
* search performance
* shard failure handling
* shard recovery
* metrics

---

## 🔬 Test Suite

Current test result:

```text
15 passed
0 failed
```

Important integration tests include:

```text
test_distributed_search
test_distributed_search_with_failed_shard
test_shard_recovery
test_search_cache
test_document_creation_invalidates_cache
test_cache_metrics
test_search_performance
```

---

## ⚡ Performance

The coordinator records latency for individual shards and the overall distributed request.

Example:

```json
{
  "shard_latency_ms": {
    "1": 32.06,
    "2": 28.95,
    "3": 27.78
  },
  "total_latency_ms": 563.78
}
```

This makes it possible to identify slow shards and analyze distributed search performance.

---

## 📈 Metrics

The application exposes metrics for monitoring search and cache behavior.

Metrics include:

* Search requests
* Cache hits
* Cache misses
* Search latency
* Shard latency
* Distributed-search behavior

The metrics endpoint can be accessed through:

```text
http://127.0.0.1:8005/metrics
```

---

## 📝 Structured Logging

The coordinator uses Python's `logging` module instead of ad-hoc `print()` statements.

Important events include:

```text
distributed_search_cache_hit
distributed_search_cache_miss
distributed_search_cache_saved
distributed_search_completed
shard_search_failed
shard_unhealthy
```

This provides better observability for distributed operations and production debugging.

---

## 🗄️ Database

PostgreSQL stores persistent document data.

Inside Docker, the API connects using:

```text
postgresql+asyncpg://postgres:postgres@postgres:5432/search_engine
```

The PostgreSQL host port is mapped to:

```text
5434
```

for local development.

---

## 🧹 Cache Management

To clear the Redis cache:

```bash
docker exec distributed-search-redis redis-cli FLUSHDB
```

Check Redis:

```bash
docker exec distributed-search-redis redis-cli PING
```

Expected:

```text
PONG
```

---

## 📸 Screenshots

### Swagger API

![Swagger API](docs/screenshots/01-swagger-api.png)

### Distributed Search

![Distributed Search](docs/screenshots/02-distributed-search.png)

### Docker Services

![Docker Services](docs/screenshots/03-docker-services.png)

### Automated Test Suite

![Automated Test Suite](docs/screenshots/04-test-suite.png)

### Metrics

![Metrics](docs/screenshots/05-metrics.png)

---

## 📡 API Endpoints

| Method   | Endpoint              | Description                    |
| -------- | --------------------- | ------------------------------ |
| `POST`   | `/documents`          | Create a document              |
| `GET`    | `/documents`          | List documents                 |
| `GET`    | `/documents/{id}`     | Get a document                 |
| `DELETE` | `/documents/{id}`     | Delete a document              |
| `GET`    | `/search`             | Local search                   |
| `GET`    | `/distributed-search` | Distributed multi-shard search |
| `GET`    | `/autocomplete`       | Search autocomplete            |
| `GET`    | `/health`             | API health check               |
| `GET`    | `/metrics`            | Application metrics            |
| `GET`    | `/docs`               | Swagger API documentation      |

---

## 🎯 Engineering Highlights

This project demonstrates practical distributed-systems concepts including:

### Distributed Query Execution

A coordinator sends search requests to multiple independent services and aggregates their responses.

### Fault Tolerance

The system continues serving results when one or more shards are unavailable.

### Service Health Monitoring

The coordinator checks shard health before executing distributed searches.

### Global Ranking

Results from independent shards are merged and ranked globally using BM25 scores.

### Caching

Redis reduces repeated computation for identical search requests.

### Pagination

Global ranking is performed before pagination to ensure users receive the highest-ranked results.

### Observability

Shard-level latency, total request latency, cache metrics, and structured logs provide visibility into system behavior.

### Containerized Deployment

The complete backend runs as a multi-service Docker Compose application.

---

## 💡 Why This Project?

Traditional single-node search systems can become bottlenecks as data and query traffic increase.

This project explores how search can be distributed across multiple independent services while maintaining:

* global ranking
* fault tolerance
* caching
* health monitoring
* pagination
* observability
* persistent storage

The architecture provides a practical foundation for understanding distributed search systems and backend scalability.

---

## 🛠️ Development Commands

### Start

```bash
docker compose up -d
```

### Rebuild

```bash
docker compose up -d --build
```

### Stop

```bash
docker compose down
```

### View logs

```bash
docker compose logs -f
```

API logs:

```bash
docker compose logs api --tail=100
```

Shard logs:

```bash
docker compose logs shard1 --tail=100
docker compose logs shard2 --tail=100
docker compose logs shard3 --tail=100
```

### Check services

```bash
docker compose ps
```

### Compile backend

```bash
docker exec distributed-search-api python -m compileall -q /app/app
```

### Run tests

```bash
docker exec distributed-search-api python -m pytest /app/tests -v
```

---

## 🧪 Verified System Status

The current project has been verified with:

```text
Docker services          ✅
PostgreSQL               ✅
Redis                    ✅
API                      ✅
Shard 1                  ✅
Shard 2                  ✅
Shard 3                  ✅
Distributed search       ✅
BM25 ranking             ✅
Pagination               ✅
Redis caching            ✅
Cache invalidation       ✅
Shard failure handling   ✅
Shard recovery           ✅
API validation           ✅
Structured logging       ✅
Healthchecks             ✅
Automated tests          ✅

Test result: 15/15 PASSED
```

---

## 📌 Project Status

**Status: Completed**

The project currently provides a working Dockerized distributed-search backend with:

* multi-shard search
* BM25 ranking
* Redis caching
* PostgreSQL persistence
* failure handling
* shard recovery
* request validation
* healthchecks
* structured logging
* automated testing
* metrics
* API documentation

---

## 👩‍💻 Author

**Sejal P**

Master of Computer Applications (MCA)

Bangalore, India

---

## ⭐ Future Improvements

Potential future extensions include:

* Elasticsearch/OpenSearch integration
* dynamic shard discovery
* automatic shard rebalancing
* replication
* leader election
* distributed tracing
* Prometheus/Grafana monitoring
* Kubernetes deployment
* load testing with Locust or k6
* query-result relevance evaluation
* LLM-based semantic reranking

---

## 📄 License

This project is intended for educational, portfolio, and distributed-systems experimentation purposes.

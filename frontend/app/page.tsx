"use client";

import { FormEvent, useState } from "react";

interface SearchResult {
  id: number;
  title: string;
  content: string;
  url: string;
  score: number;
  snippet: string;
  shard: number;
}

interface SearchResponse {
  query: string;
  total: number;
  partial: boolean;
  failed_shards: number[];
  shard_latency_ms: Record<string, number>;
  total_latency_ms: number;
  results: SearchResult[];
  cache_hit: boolean;
  cache_hits: number;
  cache_misses: number;
}

export default function Home() {
  const [query, setQuery] = useState("");
  const [data, setData] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSearch(event: FormEvent) {
    event.preventDefault();

    const trimmedQuery = query.trim();

    if (!trimmedQuery) {
      setError("Please enter a search query.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/distributed-search?q=${encodeURIComponent(
          trimmedQuery
        )}`
      );

      if (!response.ok) {
        throw new Error("Search request failed");
      }

      const result: SearchResponse = await response.json();
      setData(result);
    } catch (err) {
      console.error(err);
      setError(
        "Unable to connect to the search server. Make sure the backend is running."
      );
    } finally {
      setLoading(false);
    }
  }

  function clearSearch() {
    setQuery("");
    setData(null);
    setError("");
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-950/90">
        <div className="mx-auto max-w-6xl px-6 py-5">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold tracking-tight">
                Distributed Search
              </h1>
              <p className="text-xs text-slate-500">
                BM25 · Sharded Search · Redis
              </p>
            </div>

            <div className="flex items-center gap-2 text-sm text-green-400">
              <span className="h-2 w-2 rounded-full bg-green-400" />
              System Online
            </div>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-6xl px-6 py-14">
        {/* Hero */}
        <section className="mx-auto max-w-4xl text-center">
          <div className="mb-4 inline-flex rounded-full border border-blue-500/20 bg-blue-500/10 px-4 py-1.5 text-sm text-blue-300">
            Distributed Information Retrieval
          </div>

          <h2 className="text-4xl font-bold tracking-tight sm:text-5xl">
            Search across
            <span className="text-blue-400"> distributed shards.</span>
          </h2>

          <p className="mx-auto mt-5 max-w-2xl text-base leading-7 text-slate-400">
            A distributed search engine using BM25 ranking, parallel shard
            queries, PostgreSQL and Redis caching.
          </p>

          {/* Search */}
          <form
            onSubmit={handleSearch}
            className="mx-auto mt-9 flex max-w-3xl flex-col gap-3 sm:flex-row"
          >
            <div className="relative flex-1">
              <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-500">
                ⌕
              </span>

              <input
                type="text"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search documents..."
                className="w-full rounded-xl border border-slate-700 bg-slate-900 py-4 pl-11 pr-12 text-white outline-none transition placeholder:text-slate-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
              />

              {query && (
                <button
                  type="button"
                  onClick={clearSearch}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 transition hover:text-white"
                >
                  ×
                </button>
              )}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="rounded-xl bg-blue-600 px-8 py-4 font-semibold transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Searching..." : "Search"}
            </button>
          </form>
        </section>

        {/* Error */}
        {error && (
          <div className="mx-auto mt-6 max-w-3xl rounded-xl border border-red-900/60 bg-red-950/30 p-4 text-sm text-red-300">
            {error}
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="mx-auto mt-12 max-w-3xl text-center">
            <div className="inline-flex items-center gap-3 rounded-xl border border-slate-800 bg-slate-900 px-5 py-4 text-sm text-slate-400">
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-600 border-t-blue-400" />
              Querying distributed shards...
            </div>
          </div>
        )}

        {/* Results */}
        {data && !loading && (
          <section className="mt-14">
            {/* Metrics */}
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <MetricCard
                label="Results"
                value={String(data.total)}
                description="Documents found"
              />

              <MetricCard
                label="Latency"
                value={`${data.total_latency_ms} ms`}
                description="Total search time"
              />

              <MetricCard
                label="Cache"
                value={data.cache_hit ? "HIT" : "MISS"}
                description={`${data.cache_hits} hits · ${data.cache_misses} misses`}
                valueClass={
                  data.cache_hit ? "text-green-400" : "text-yellow-400"
                }
              />

              <MetricCard
                label="Status"
                value={data.partial ? "PARTIAL" : "COMPLETE"}
                description={
                  data.partial
                    ? `${data.failed_shards.length} shard(s) unavailable`
                    : "All shards responded"
                }
                valueClass={
                  data.partial ? "text-yellow-400" : "text-green-400"
                }
              />
            </div>

            {/* Shard Performance */}
            <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900/70 p-6">
              <div className="mb-5 flex items-center justify-between">
                <div>
                  <h3 className="font-semibold">Shard Performance</h3>
                  <p className="mt-1 text-sm text-slate-500">
                    Parallel search across three shards
                  </p>
                </div>

                <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-400">
                  3 Shards
                </span>
              </div>

              <div className="grid gap-3 md:grid-cols-3">
                {["1", "2", "3"].map((shard) => {
                  const failed = data.failed_shards.includes(Number(shard));
                  const latency = data.shard_latency_ms[shard];

                  return (
                    <div
                      key={shard}
                      className="rounded-xl border border-slate-800 bg-slate-950 p-5 transition hover:border-slate-700"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-medium">Shard {shard}</span>

                        <span
                          className={`flex items-center gap-1.5 text-sm ${
                            failed ? "text-red-400" : "text-green-400"
                          }`}
                        >
                          <span
                            className={`h-2 w-2 rounded-full ${
                              failed ? "bg-red-400" : "bg-green-400"
                            }`}
                          />
                          {failed ? "Failed" : "Healthy"}
                        </span>
                      </div>

                      <div className="mt-4">
                        <p className="text-2xl font-semibold">
                          {failed ? "—" : `${latency ?? "-"} ms`}
                        </p>
                        <p className="mt-1 text-xs text-slate-500">
                          Response latency
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Result heading */}
            <div className="mb-5 mt-10 flex items-end justify-between">
              <div>
                <p className="text-sm text-slate-500">Search results</p>
                <h3 className="mt-1 text-2xl font-semibold">
                  Results for{" "}
                  <span className="text-blue-400">"{data.query}"</span>
                </h3>
              </div>

              <span className="hidden text-sm text-slate-500 sm:block">
                Ranked by BM25
              </span>
            </div>

            {/* Result list */}
            <div className="space-y-4">
              {data.results.length === 0 ? (
                <div className="rounded-2xl border border-slate-800 bg-slate-900 p-12 text-center">
                  <div className="text-4xl">⌕</div>
                  <h3 className="mt-4 font-semibold">No results found</h3>
                  <p className="mt-2 text-sm text-slate-500">
                    Try a different search term.
                  </p>
                </div>
              ) : (
                data.results.map((result, index) => (
                  <article
                    key={result.id}
                    className="group rounded-2xl border border-slate-800 bg-slate-900/70 p-6 transition hover:border-blue-500/40 hover:bg-slate-900"
                  >
                    <div className="flex flex-col gap-4">
                      <div className="flex flex-col justify-between gap-4 sm:flex-row">
                        <div>
                          <div className="mb-2 flex items-center gap-2">
                            <span className="text-xs text-slate-600">
                              #{index + 1}
                            </span>

                            <span className="rounded-full bg-purple-500/10 px-2.5 py-1 text-xs text-purple-300">
                              Shard {result.shard}
                            </span>
                          </div>

                          <h4 className="text-xl font-semibold text-blue-400 transition group-hover:text-blue-300">
                            {result.title}
                          </h4>

                          <a
                            href={result.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="mt-1 block break-all text-sm text-green-400 hover:underline"
                          >
                            {result.url}
                          </a>
                        </div>

                        <div className="shrink-0">
                          <span className="rounded-full bg-blue-500/10 px-3 py-1.5 text-xs font-medium text-blue-300">
                            BM25 {result.score}
                          </span>
                        </div>
                      </div>

                      <p className="border-t border-slate-800 pt-4 leading-7 text-slate-300">
                        {result.snippet}
                      </p>
                    </div>
                  </article>
                ))
              )}
            </div>
          </section>
        )}

        {/* Initial state */}
        {!data && !loading && !error && (
          <section className="mx-auto mt-20 max-w-3xl text-center">
            <div className="rounded-2xl border border-dashed border-slate-800 bg-slate-900/40 p-12">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-500/10 text-2xl text-blue-400">
                ⌕
              </div>

              <h3 className="mt-5 text-lg font-semibold">
                Start searching
              </h3>

              <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">
                Enter a query above to search across all three distributed
                shards using BM25 ranking.
              </p>
            </div>
          </section>
        )}
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-800">
        <div className="mx-auto max-w-6xl px-6 py-6 text-center text-xs text-slate-600">
          Distributed Search Engine · FastAPI · PostgreSQL · Redis · Docker ·
          Next.js
        </div>
      </footer>
    </main>
  );
}

function MetricCard({
  label,
  value,
  description,
  valueClass = "text-white",
}: {
  label: string;
  value: string;
  description: string;
  valueClass?: string;
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-5">
      <p className="text-sm text-slate-500">{label}</p>

      <p className={`mt-2 text-2xl font-semibold ${valueClass}`}>{value}</p>

      <p className="mt-1 text-xs text-slate-600">{description}</p>
    </div>
  );
}
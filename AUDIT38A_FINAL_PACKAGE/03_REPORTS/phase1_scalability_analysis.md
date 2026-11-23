# Phase I Architecture Scalability Analysis: 5,000 to 500,000+ Records

**Generated:** 2026-11-22T14:23:03.512991+00:00  
**Architectural Scope:** SQLite Baseline -> Partitioned PostgreSQL / ClickHouse Scale-Out  

---

## 1. Current Baseline vs Enterprise Target Architecture

| Architectural Dimension | Current Baseline (~6,745 Records) | Intermediate Target (50,000 Records) | Enterprise Scale (500,000+ Records) |
|---|---|---|---|
| **Storage Engine** | Single SQLite3 File (`ai_ecosystem.db`, 21.2 MB) | SQLite with WAL mode & tuned page sizes | Distributed PostgreSQL (Citus / TimescaleDB) or ClickHouse |
| **Ingestion Throughput** | ~50 records/sec (Single thread) | ~500 records/sec (Async HTTPX connection pooling) | ~5,000 records/sec (Kafka / RabbitMQ ingest workers) |
| **Deduplication Engine** | In-memory sets (O(N) RAM overhead) | SQLite Unique B-Tree Indexes on SHA-256 hashes | Redis Bloom Filters + Distributed Hash Indexing |
| **GitHub API Verification** | Direct REST API (5,000 req/hr token limit) | ETag caching + conditional 304 requests | GitHub GraphQL batching + Multi-token rotation pool |
| **Search & Retrieval** | SQLite `LIKE` & full-text match | SQLite FTS5 Virtual Tables | Elasticsearch / OpenSearch + Qdrant / Pinecone Vectors |
| **Storage Footprint** | ~21.2 MB | ~160 MB | ~1.6 GB relational + ~8 GB vector embeddings |

## 2. Ingestion & Enrichment Scaling Strategy

### A. GitHub Rate Limit Scaling (5,000 requests/hour limit)
At 500,000 research papers, query capacity requires structured rate optimization:
1. **ETag / Conditional HTTP Headers (`If-None-Match`):** Returns HTTP 304 (Not Modified) which costs 0 rate-limit quota on unmodified repositories.
2. **GraphQL API Batching:** Consolidates 100 repository star queries into a single HTTP POST request, increasing throughput by 100x.
3. **Staggered Crawl Cycles:** Updates top-tier repos (stars > 10,000) daily, mid-tier (stars > 100) weekly, and long-tail repos monthly.

### B. Memory and Storage Efficiency
- **Zero-Copy Streaming:** Ingestion pipelines utilize generator streams (`yield`) rather than loading batches into RAM.
- **Deterministic Storage Partitioning:** Partition tables by ingestion year/month (`ai_research_papers_2026_11`).
- **Foreign Key & Index Optimization:** Covered B-tree indices on `(entity_name, primary_source_url)` ensure O(log N) lookup latency at 500k rows.

## 3. Cost Projection at 500,000 Records

| Resource Component | Ingestion & Storage Cost (Monthly) | Enrichment API Cost |
|---|:---:|:---:|
| Managed PostgreSQL (AWS RDS / Supabase) | ~$120.00 / mo | — |
| Object Storage (S3 / R2 for HTML snapshots) | ~$15.00 / mo | — |
| GitHub REST / GraphQL API | $0.00 (Enterprise PAT allowance) | $0.00 |
| Primary LLM Verification (Gemini 1.5 Flash batch) | — | ~$45.00 / 100k records |
| **Total Estimated Monthly Infrastructure** | **~$135.00 / mo** | **Scalable on-demand** |

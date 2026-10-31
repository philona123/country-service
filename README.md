# Country Service

A GraphQL API for country data backed by **MongoDB**, with **Redis** caching on single-country reads and periodic ingestion from [countries.dev](https://countries.dev).

## Stack

- FastAPI + Strawberry GraphQL
- MongoDB (`country_db.countries`)
- Redis (optional; degrades gracefully if unavailable)
- APScheduler for scheduled ingestion

## Prerequisites

Python 3.12+, [uv](https://docs.astral.sh/uv/) (or pip + venv), Docker.

## Setup

```bash
cd country-service
cp .env.example .env   # edit if needed
docker compose up -d
uv sync --all-groups
```

With pip instead of uv: `python -m venv venv && source venv/bin/activate && pip install -r requirements.txt`

## Run

```bash
uv run dev
```

On startup the API connects to Mongo/Redis and creates indexes, then **accepts requests immediately**. The first countries sync runs in a **background asyncio task** (same process); scheduled ingestion uses APScheduler. Until that first sync finishes, list/country queries may be empty.

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/graphql | GraphQL + schema docs |
| http://127.0.0.1:8000/health | Health (`cache_enabled` = Redis OK) |

## GraphQL

Resolver names are **camelCase** in the schema (e.g. `getCountryByCode`, `createCountry`).

**Queries:** `getCountries`, `getCountryByCode`, `getCountryById`, `getCountriesByLanguage`, `getNearbyCountries`, `getCountriesGroupedByCurrency`

**Mutations:**
- `createCountry(input)` — required in input: `code`, `commonName`, `officialName`; other fields optional
- `updateCountry(id, code, input)` — pass **`id` or `code`** (if both, **id** wins); `input` is name fields only (`commonName`, `officialName`, `nativeName`, at least one)

Use the GraphQL playground for full types and to try queries.

## Tests

Unit tests (no Mongo required):

```bash
uv run test
```

Integration tests (Test MongoDB required):

```bash
uv run test-integration
```

Run all tests:

```bash
uv run test-all
```

Integration tests are skipped automatically if MongoDB is unreachable.

## Configuration

See `.env.example` for all variables (Mongo, Redis, cache TTL, ingestion interval, log level).

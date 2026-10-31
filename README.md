# Country Service

A GraphQL API for country data backed by **MongoDB**, with **Redis** caching on single-country reads and periodic ingestion from [countries.dev](https://countries.dev).

## Stack

- FastAPI + Strawberry GraphQL
- MongoDB (`country_db.countries`)
- Redis (optional; degrades gracefully if unavailable)
- APScheduler for scheduled ingestion

## Prerequisites

- Python 3.12+
- Docker (MongoDB and Redis)

## Setup

### Option A: uv (recommended)

Install [uv](https://docs.astral.sh/uv/), then:

```bash
cd country-service
uv sync --all-groups
docker compose up -d
```

### Option B: venv + pip

```bash
cd country-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
docker compose up -d
```

Copy or edit `.env` in the project root (see variables below).

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URI` | Mongo connection string | `mongodb://localhost:27017` |
| `MONGODB_DATABASE` | Database name | `country_db` |
| `REDIS_URL` | Redis URL | `redis://localhost:6379/0` |
| `CACHE_ENABLED` | Enable Redis cache | `true` |
| `CACHE_TTL_SECONDS` | Entity cache TTL | `300` |
| `COUNTRY_API_URL` | Ingestion source base URL | `https://countries.dev` |
| `INGESTION_INTERVAL_HOURS` | Scheduled sync interval | `24` |
| `LOG_LEVEL` | Logging level | `INFO` |

On startup the app connects to MongoDB and Redis, creates indexes, runs an initial country ingestion, and starts the ingestion scheduler.

## Run

From the `country-service` directory (entrypoint is `app/main.py`):

```bash
# uv (uses project .venv; deactivate an old `venv` first to avoid warnings)
uv run dev

# equivalent
uv run fastapi dev app/main.py

# venv + pip
fastapi dev app/main.py
```

| Endpoint | Purpose |
|----------|---------|
| `http://127.0.0.1:8000/graphql` | GraphQL (playground in dev) |
| `http://127.0.0.1:8000/health` | Health check (`cache_enabled` reflects Redis) |

## GraphQL API

Field names in GraphQL use **camelCase** (Python resolvers use `snake_case`).

### Queries

| Field | Arguments | Returns |
|-------|-----------|---------|
| `getCountries` | `page`, `pageSize` (defaults 1, 10) | Paginated `CountryConnection` |
| `getCountryByCode` | `code` (ISO 2-letter) | `Country` or null |
| `getCountryById` | `id` (Mongo ObjectId string) | `Country` or null |
| `getCountriesByLanguage` | `language` | List of `Country` |
| `getNearbyCountries` | `latitude`, `longitude`, `maxDistance` (default 500 km) | List of `{ country, distanceKm }` |
| `getCountriesGroupedByCurrency` | — | List of currency groups with countries |

### Mutations

| Field | Input | Returns |
|-------|-------|---------|
| `createCountry` | `AddCountryInput` — required: `code`, `commonName`, `officialName`; optional region, population, capital, geo, currencies, languages, etc. | `Country` |
| `updateCountry` | `id` or `code` (if both, **id** wins); `input`: at least one of `commonName`, `officialName`, `nativeName` | `Country` |

### Example: country by code

```graphql
query {
  getCountryByCode(code: "IN") {
    id
    code
    name {
      common
      official
    }
    population
    capital
  }
}
```

### Example: create country

```graphql
mutation {
  createCountry(
    input: {
      code: "XX"
      commonName: "Exampleland"
      officialName: "Republic of Exampleland"
    }
  ) {
    code
    name {
      common
    }
  }
}
```

Use the schema docs in the GraphQL UI for the full `Country` type and input shapes.

### Example: update country by code or id

```graphql
mutation UpdateByCode {
  updateCountry(
    code: "IN"
    input: {
      commonName: "India"
      officialName: "Republic of India"
    }
  ) {
    id
    code
    name {
      common
      official
    }
  }
}
```

```graphql
mutation UpdateById {
  updateCountry(
    id: "507f1f77bcf86cd799439011"
    input: { nativeName: "भारत" }
  ) {
    code
    name {
      native
    }
  }
}
```

Provide **`id` or `code`** (not neither). If both are sent, **`id` is used**.

## Tests

```bash
uv run test
# or: uv run pytest tests/unit -v
```

Unit tests mock MongoDB and Redis; no running services required.

## Project layout (brief)

```
app/
  main.py              # FastAPI app, lifespan, /health
  resolvers/           # GraphQL queries & mutations
  services/            # Business logic + cache orchestration
  repositories/        # MongoDB access
  cache/               # Redis client and country cache
  ingestion/           # External API client, transform, scheduler
  graphql/             # Schema types and inputs
  schemas/             # Pydantic validation DTOs
  utils/               # GraphQL ↔ DTO mapping, document builders
```

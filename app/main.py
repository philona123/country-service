import logging
from contextlib import asynccontextmanager
from app.config import settings
from app.logging_config import configure_logging

configure_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from app.database.connection import (
    connect_to_database,
    close_database_connection
)
from app.cache.connection import connect_to_redis, close_redis_connection
from app.database.indexes import create_indexes
from app.graphql.schema import schema
from app.ingestion.scheduler import (
    start_scheduler,
    stop_scheduler
)
from app.services.ingestion_service import ingest_countries

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_database()
    await connect_to_redis()
    await create_indexes()
    try:
        await ingest_countries()
    except Exception as error:
        logger.error(f"Initial ingestion failed: {error}")
    start_scheduler()
    yield
    stop_scheduler()
    await close_redis_connection()
    await close_database_connection()


app = FastAPI(
    title="Country Information API",
    description="Country information service using GraphQL and MongoDB",
    version="1.0.0",
    lifespan=lifespan
)


graphql_router = GraphQLRouter(schema)

app.include_router(
    graphql_router,
    prefix="/graphql"
)


@app.get("/health")
async def health():
    from app.cache.connection import is_cache_available

    return {
        "status": "healthy",
        "cache_enabled": is_cache_available(),
    }
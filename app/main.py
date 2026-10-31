import asyncio
import contextlib
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from app.cache.connection import close_redis_connection, connect_to_redis
from app.config import settings
from app.database.connection import close_database_connection, connect_to_database
from app.database.indexes import create_indexes
from app.graphql.schema import schema
from app.ingestion.scheduler import start_scheduler, stop_scheduler
from app.logging_config import configure_logging
from app.services.ingestion_service import ingest_countries

configure_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


async def _run_startup_ingestion() -> None:
    try:
        await ingest_countries()
    except Exception as error:
        logger.error("Startup ingestion failed: %s", error)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_database()
    await connect_to_redis()
    await create_indexes()

    startup_ingestion_task = asyncio.create_task(
        _run_startup_ingestion(),
        name="startup_ingestion",
    )
    start_scheduler()
    yield
    stop_scheduler()
    startup_ingestion_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await startup_ingestion_task
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
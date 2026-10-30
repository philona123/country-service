from contextlib import asynccontextmanager

from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from app.database.connection import (
    connect_to_database,
    close_database_connection
)

from app.database.indexes import create_indexes

from app.graphql.schema import schema

from app.ingestion.scheduler import (
    start_scheduler,
    stop_scheduler
)

from app.services.ingestion_service import ingest_countries


@asynccontextmanager
async def lifespan(app: FastAPI):

    # 1. Connect to MongoDB
    await connect_to_database()

    # 2. Create indexes
    await create_indexes()

    # 3. Perform initial ingestion
    try:
        await ingest_countries()
    except Exception as error:
        print(f"Initial ingestion failed: {error}")

    # 4. Start periodic ingestion
    start_scheduler()

    yield

    # Shutdown
    stop_scheduler()

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
    return {
        "status": "healthy"
    }
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.services.ingestion_service import ingest_countries

scheduler = AsyncIOScheduler()


def start_scheduler() -> None:
    scheduler.add_job(
        ingest_countries,
        trigger="interval",
        hours=settings.INGESTION_INTERVAL_HOURS,
        id="country_ingestion",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)

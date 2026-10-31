import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.services.ingestion_service import ingest_countries

logger = logging.getLogger(__name__)

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
    # Log the next country ingestion scheduled time
    job = scheduler.get_job("country_ingestion")
    if job and job.next_run_time:
        logger.info(
            "Next country ingestion scheduled at %s (every %s hours)",
            job.next_run_time,
            settings.INGESTION_INTERVAL_HOURS,
        )


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)

import asyncio
import logging
import os
import time
from datetime import datetime

from sqlmodel import Session, SQLModel, select
from starlette.concurrency import run_in_threadpool

from ..datatypes import ArtmuseumTimeLabel
from ..scraping.artmuseum import scrap_artmuseum
from ..scraping.philharmonia import scrap_philharmonia
from .models import ArtmuseumExhibition, PhilharmoniaConcert


def refresh_data(engine):
    """
    Scrap all the data sources for up-to-date info. Drop local values and replace them with the new data.

    We are trying to be an exact mirror of our data sources.
    The easiest way to achieve this is to regularly throw out all the data we have and scrap up-to-date info.
    The cost of this approach in performance/resources is neglectable and is much preffered over complications
    brought by trying to maintain a local copy by continuously patching it up with UPDATEs.
      (there can be edits in the source info, urls can change, etc. - it's not worth it to consider all such corner cases)
    """
    logging.info("Started scraping up-to-date info.")
    known_addrs = {}
    with Session(engine) as session:
        stmt = select(ArtmuseumExhibition.url, ArtmuseumExhibition.address).where(
            ArtmuseumExhibition.address != None
        )
        known_addrs = dict(session.exec(stmt).all())
    exhibitions = scrap_artmuseum(known_addrs)
    concerts = scrap_philharmonia()
    logging.info("Finished scraping up-to-date info.")

    logging.info("Started updating the database.")
    with Session(engine) as session:
        session.query(PhilharmoniaConcert).delete()
        session.query(ArtmuseumExhibition).delete()

        session.bulk_save_objects(concerts)
        session.bulk_save_objects(exhibitions)

        session.commit()
    logging.info("Finished updating the database.")


async def loop_refreshing_data(engine, update_interval, initial_sleep_time: int = 0):
    if initial_sleep_time > 0:
        await asyncio.sleep(initial_sleep_time)
    while True:
        await run_in_threadpool(refresh_data, engine)
        await asyncio.sleep(update_interval)


def init_db(engine):
    update_interval = 60 * 60 * 8  # 8 hours
    initial_sleep_time = 0

    if os.path.isfile(engine.url.database):
        last_modified = os.path.getmtime(engine.url.database)
        dt = time.time() - last_modified

        if dt <= update_interval:
            initial_sleep_time = update_interval - dt

            last_update = datetime.fromtimestamp(last_modified).replace(microsecond=0)
            logging.info(
                f"Last database update - {last_update}, the next one is scheduled in ...[N]h [N]m.... (at h:m)"
            )

    SQLModel.metadata.create_all(engine)

    asyncio.create_task(
        loop_refreshing_data(engine, update_interval, initial_sleep_time)
    )

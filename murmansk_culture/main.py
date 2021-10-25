import asyncio
import logging
import os
import pickle
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse

# from scraping import artmuseum
from scraping.artmuseum import Exhibition, TimeLabel, scrap_exhibitions
from starlette.concurrency import run_in_threadpool

Seconds = int

# TODO: exception handling
@dataclass
class Exhibitions:
    """
    A singleton that represents all the scraped exhibitions.
    The instance of Exhibitions is initialized at startup and is
      always available as a global variable.
    """

    current: list[Exhibition] = field(default_factory=list)
    upcoming: list[Exhibition] = field(default_factory=list)
    filename: str = "exhibitions.pickle"
    update_interval: Seconds = 60 * 60 * 8  # 8 hours

    def scrap_and_save(self):
        self.current = scrap_exhibitions(
            TimeLabel.NOW, {exh.url: exh.address for exh in self.current}
        )
        self.upcoming = scrap_exhibitions(
            TimeLabel.SOON, {exh.url: exh.address for exh in self.upcoming}
        )
        logging.info("Scraped exhibitions")

        with open(self.filename, "wb") as file:
            pickle.dump(exhibitions, file)
        logging.info(f"Saved exhibitions data to {self.filename}")

    def load(self):
        with open(self.filename, "rb") as file:
            data = pickle.load(file)
            self.current = data.current
            self.upcoming = data.upcoming
        logging.info(f"Loaded exhibitions data from {self.filename}")

    # TODO: parse rss feed for updates? (still need scraping on startup)
    async def loop_scraping(self, wait_first: bool = True):
        """Scrap again to update the data once every {self.update_interval} seconds."""
        if wait_first:
            await asyncio.sleep(self.update_interval)
        while True:
            await run_in_threadpool(self.scrap_and_save)
            await asyncio.sleep(self.update_interval)


exhibitions = Exhibitions()

app = FastAPI(redoc_url="/api/docs", docs_url=None)


@app.on_event("startup")
def startup():
    if os.path.isfile(exhibitions.filename):
        exhibitions.load()

        last_modified = os.path.getmtime(exhibitions.filename)
        dt = time.time() - last_modified

        if timedelta(seconds=dt) > timedelta(seconds=exhibitions.update_interval):
            logging.info(
                f"The {exhibitions.filename} file is not up-to-date, scraping new data."
            )
            exhibitions.scrap_and_save()
        else:
            last_update = datetime.fromtimestamp(last_modified).replace(microsecond=0)
            logging.info(
                f"The {exhibitions.filename} file is up-to-date, last update - {last_update}"
            )
    else:
        logging.info(f"No {exhibitions.filename} file found, scraping new data.")
        exhibitions.scrap_and_save()

    # TODO: first update should be based on the last one
    asyncio.create_task(exhibitions.loop_scraping())


@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse("https://github.com/anorlovsky/artmuseum")


@app.get("/api", response_model=list[Exhibition])
async def serve_exhibitions(time: TimeLabel = None):
    if time is None:
        return exhibitions.current + exhibitions.upcoming
    if time == TimeLabel.NOW:
        return exhibitions.current
    if time == TimeLabel.SOON:
        return exhibitions.upcoming

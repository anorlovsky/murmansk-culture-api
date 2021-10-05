import os
import time
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import pickle

from fastapi import FastAPI, Query
from starlette.concurrency import run_in_threadpool

from scrap import TimeLabel, Exhibition, scrap_exhibitions

Seconds = int

# TODO: add proper logging
# TODO: exception handling
# TODO?: parse rss feed for updates? (still need scraping on startup)
# ?: do I want to use a db here?
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
        print("Scraped exhibitions")

        with open(self.filename, "wb") as file:
            pickle.dump(exhibitions, file)
        print(f"Saved exhibitions data to {self.filename}")

    def load(self):
        with open(self.filename, "rb") as file:
            data = pickle.load(file)
            self.current = data.current
            self.upcoming = data.upcoming
        print(f"Loaded exhibitions data from {self.filename}")

    async def loop_scraping(self, wait_first: bool = True):
        """Scrap again to update the data once every {self.update_interval} seconds."""
        if wait_first:
            await asyncio.sleep(self.update_interval)
        while True:
            await run_in_threadpool(self.scrap_and_save)
            await asyncio.sleep(self.update_interval)


exhibitions = Exhibitions()

app = FastAPI()


@app.on_event("startup")
def startup():
    if os.path.isfile(exhibitions.filename):
        exhibitions.load()

        last_modified = os.path.getmtime(exhibitions.filename)
        dt = time.time() - last_modified

        if timedelta(seconds=dt) > timedelta(seconds=exhibitions.update_interval):
            print(
                f"The {exhibitions.filename} file is not up-to-date, scraping new data."
            )
            exhibitions.scrap_and_save()
        else:
            last_update = datetime.fromtimestamp(last_modified).replace(microsecond=0)
            print(
                f"The {exhibitions.filename} file is up-to-date, last update - {last_update}"
            )
    else:
        print(f"No {exhibitions.filename} file found, scraping new data.")
        exhibitions.scrap_and_save()

    asyncio.create_task(exhibitions.loop_scraping())


# TODO: '/docs' -> '/api/docs'
@app.get("/api", response_model=list[Exhibition])
async def serve_exhibitions(time: TimeLabel = None):
    if time is None:
        return exhibitions.current + exhibitions.upcoming
    if time == TimeLabel.NOW:
        return exhibitions.current
    if time == TimeLabel.SOON:
        return exhibitions.upcoming

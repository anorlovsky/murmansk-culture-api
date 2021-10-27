import asyncio
import logging
import os
import pickle
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse
from starlette.concurrency import run_in_threadpool

from scraping.artmuseum import Exhibition, TimeLabel, scrap_exhibitions

Seconds = int

# TODO: use sqlalchemy with sqlite backend (once you finish their tutorial)
# TODO: concurrent scraping
#   The slowest part is address scraping for artmuseum - there's >20 pages to request, let's do that in a threadpool.
#   Parsing them for addrs might be slow too, but I can't multiprocess that since my server has only one processor.
@dataclass
class Data:
    current_exhibitions: list[Exhibition] = field(default_factory=list)
    upcoming_exhibitions: list[Exhibition] = field(default_factory=list)
    filename: str = "data.pickle"
    update_interval: Seconds = 60 * 60 * 8  # 8 hours

    def scrap_and_save(self):
        self.current_exhibitions = scrap_exhibitions(TimeLabel.NOW, scrap_addrs=False)
        self.upcoming_exhibitions = scrap_exhibitions(TimeLabel.SOON, scrap_addrs=False)
        # self.current_exhibitions = scrap_exhibitions(
        #     TimeLabel.NOW, {exh.url: exh.address for exh in self.current_exhibitions}
        # )
        # self.upcoming_exhibitions = scrap_exhibitions(
        #     TimeLabel.SOON, {exh.url: exh.address for exh in self.upcoming_exhibitions}
        # )
        logging.info("Scraped data")

        with open(self.filename, "wb") as file:
            pickle.dump(self, file)
        logging.info(f"Saved data to {self.filename}")

    def load(self):
        with open(self.filename, "rb") as file:
            data = pickle.load(file)
            self.current_exhibitions = data.current_exhibitions
            self.upcoming_exhibitions = data.upcoming_exhibitions
        logging.info(f"Loaded data from {self.filename}")

    async def loop_scraping(self, wait_first: bool = True):
        """Scrap again to update the data once every {self.update_interval} seconds."""
        if wait_first:
            await asyncio.sleep(self.update_interval)
        while True:
            await run_in_threadpool(self.scrap_and_save)
            await asyncio.sleep(self.update_interval)


# TODO: move under __name__ == '__main__'
data = Data()

app = FastAPI(redoc_url="/api/docs", docs_url=None)


@app.on_event("startup")
def load_data():
    if os.path.isfile(data.filename):
        data.load()

        last_modified = os.path.getmtime(data.filename)
        dt = time.time() - last_modified

        if timedelta(seconds=dt) > timedelta(seconds=data.update_interval):
            logging.info(
                f"The {data.filename} file is not up-to-date, scraping new data."
            )
            data.scrap_and_save()
        else:
            last_update = datetime.fromtimestamp(last_modified).replace(microsecond=0)
            logging.info(
                f"The {data.filename} file is up-to-date, last update - {last_update}"
            )
    else:
        logging.info(f"No {data.filename} file found, scraping new data.")
        data.scrap_and_save()

    # TODO: first update should be based on the last one
    asyncio.create_task(data.loop_scraping())


@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse("https://github.com/anorlovsky/artmuseum")


@app.get("/api", response_model=list[Exhibition])
async def serve_exhibitions(time: TimeLabel = None):
    if time is None:
        return data.current_exhibitions + data.upcoming_exhibitions
    if time == TimeLabel.NOW:
        return data.current_exhibitions
    if time == TimeLabel.SOON:
        return data.upcoming_exhibitions


# @app.get("/api/artmuseum", response_model=list[ArtmuseumExhibition])
# async def serve_artmuseum(time: TimeLabel = None):
#     if time is None:
#         return data.current + data.upcoming
#     if time == TimeLabel.NOW:
#         return data.current
#     if time == TimeLabel.SOON:
#         return data.upcoming


# @app.get("/api/philharmonia", response_model=list[PhilharmoniaConcert])
# async def serve_philharmonia():

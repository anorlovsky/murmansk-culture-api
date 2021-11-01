import asyncio
import logging
import os
import pickle
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from starlette.concurrency import run_in_threadpool

from scraping.artmuseum import Exhibition, TimeLabel, scrap_artmuseum
from scraping.philharmonia import PhilharmoniaConcert, scrap_philharmonia

Seconds = int

# TODO: use sqlalchemy with sqlite backend (once you finish their tutorial)
# TODO: concurrent scraping
#   The slowest part is address scraping for artmuseum - there's >20 pages to request, let's do that in a threadpool.
#   Parsing them for addrs might be slow too, but I can't multiprocess that since my server has only one processor.
@dataclass
class Data:
    current_exhibitions: list[Exhibition] = field(default_factory=list)
    upcoming_exhibitions: list[Exhibition] = field(default_factory=list)
    concerts: list[PhilharmoniaConcert] = field(default_factory=list)
    filename: str = "data.pickle"
    update_interval: Seconds = 60 * 60 * 8  # 8 hours

    # TODO: break it up, there are too much implicit things going on there
    def init(self):
        if os.path.isfile(self.filename):
            self.load()

            last_modified = os.path.getmtime(self.filename)
            dt = time.time() - last_modified

            if timedelta(seconds=dt) > timedelta(seconds=self.update_interval):
                logging.info(
                    f"The {self.filename} file is not up-to-date, scraping new data."
                )
                self.scrap_and_save()
            else:
                last_update = datetime.fromtimestamp(last_modified).replace(
                    microsecond=0
                )
                logging.info(
                    f"The {self.filename} file is up-to-date, last update - {last_update}"
                )
        else:
            logging.info(f"No {self.filename} file found, scraping new data.")
            self.scrap_and_save()

        return self

    def scrap_and_save(self):
        self.current_exhibitions = scrap_artmuseum(
        TimeLabel.NOW, scraped_addrs={exh.url: exh.address for exh in self.current_exhibitions}
        )
        self.upcoming_exhibitions = scrap_artmuseum(
        TimeLabel.SOON, scraped_addrs={exh.url: exh.address for exh in self.upcoming_exhibitions}
        )
        # self.current_exhibitions = scrap_artmuseum(TimeLabel.NOW, scrap_addrs=False)
        # self.upcoming_exhibitions = scrap_artmuseum(TimeLabel.SOON, scrap_addrs=False)
        self.concerts = scrap_philharmonia()

        logging.info("Scraped data")

        with open(self.filename, "wb") as file:
            pickle.dump(self, file)
        logging.info(f"Saved data to {self.filename}")

    def load(self):
        with open(self.filename, "rb") as file:
            data = pickle.load(file)
            self.current_exhibitions = data.current_exhibitions
            self.upcoming_exhibitions = data.upcoming_exhibitions
            self.concerts = data.concerts
        logging.info(f"Loaded data from {self.filename}")

    async def loop_scraping(self, wait_first: bool = True):
        """Scrap again to update the data once every {self.update_interval} seconds."""
        if wait_first:
            await asyncio.sleep(self.update_interval)
        while True:
            await run_in_threadpool(self.scrap_and_save)
            await asyncio.sleep(self.update_interval)

from enum import Enum, auto
from dataclasses import dataclass
from datetime import datetime

import requests
from bs4 import BeautifulSoup


""" NOTE(anorlovsky)
Rough plan for the project:
- initially - a couple API endpoints (FastAPI) to return the current and future exhibitions of Murmansk Art Museum (https://artmmuseum.ru/)
- eventually (conditional on me staying in Murmansk):
    - build a Telegram bot on top of that
    - extend it with other cultural events (like philharmonia concerts, theater plays, etc.)
    - use rss feeds over web scrapping whenever it's possible (run scrapping on startup, then schedule RSS-based updates)
"""

# TODO: write down all the gotchas with parsing the artmmuseum website (corner cases like wrong dates, etc., I sketched some in personal notes)


class Address(Enum):
    MUSEUM = auto()
    PHILHARMONIA = auto()
    DOMREMESEL = auto()
    UNKNOWN = auto()


# @dataclass
# class Exhibition:
#     title: str
#     start_date: datetime
#     end_date: datetime
#     address: Address


def parse_address(url: str):
    word_bag: dict[Address, list[str]] = {
        Address.MUSEUM: ["коминтерна", "главном здании"],
        Address.PHILHARMONIA: ["перовской", "филарм", "культурно-выставочн"],
        Address.DOMREMESEL: ["книповича"],
    }

    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    text = soup.find("div", {"class": "entry"}).text.lower()

    for address, keywords in word_bag.items():
        if any(kw in text for kw in keywords):
            return address

    return address.UNKNOWN


# TODO: run once on startup, then - schedule for every X hours (12?)
def scrap_current_exhibitions():
    # TODO: scrap all "current exhibitions" pages, not just the first one
    res = requests.get("https://artmmuseum.ru/category/vystavki/tekushhie-vystavki")
    soup = BeautifulSoup(res.text, "html.parser")

    exhibitions = soup.find_all("h1", {"class": "h-exibition"})

    # TODO: filter out '<span class="label_archive">' -
    #  sometimes it stays on the "current exhibitions" page for a while
    entries = []
    for exh in exhibitions:
        entry = {}

        title = exh.find("a", {"class": "link"})["title"]
        # they prepend "Выставка" to every title attribute, which often leads
        #  to cases like "Выставка Выставка живописи ..."
        title = title.removeprefix("Выставка ")
        # TODO: convert 0xa0 (Windows 1251?) to whitespace
        entry["title"] = title

        url = exh.find("a", {"class": "link"})["href"]
        entry["url"] = url

        # sometimes exhibitions are published with a single date
        #  (although in fact it might have start date and end date specified on the exhibition page)
        if (date := exh.find("time", {"itemprop": "datePublished"})) is not None:
            date = date["datetime"]
            entry["date"] = date
        else:
            start_date = exh.find("time", {"itemprop": "startDate"})["datetime"]
            end_date = exh.find("time", {"itemprop": "endDate"})["datetime"]
            entry["start_date"] = start_date
            entry["end_date"] = end_date
            entry["address"] = parse_address(url)

        entries.append(entry)

    for entry in entries:
        for x in entry.values():
            print(x)
        print("\n")


if __name__ == "__main__":
    scrap_current_exhibitions()

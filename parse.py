from enum import Enum, auto
from dataclasses import dataclass
from datetime import date, datetime

from pydantic import BaseModel

import json

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


class Address(str, Enum):
    MUSEUM = "Мурманский областной художественный музей (ул. Коминтерна, д.13)"
    PHILHARMONIA = (
        "Культурно-выставочный центр Русского музея (Мурманская областная филармония"
        " - ул. Софьи Перовской, д. 3, второй этаж)"
    )
    DOMREMESEL = (
        "Отдел народного искусства и ремёсел (Дом Ремёсел - ул. Книповича, д. 23А)"
    )
    UNKNOWN = "неизвестно"


class Exhibition(BaseModel):
    title: str
    url: str
    start_date: date
    end_date: date
    address: Address = None


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


# TODO: separate function for parsing individual entries (purpose: easier testability)
# TODO: run once on startup, then - schedule for every X hours (12?)
def scrap_current_exhibitions(include_address=True):
    res = requests.get("https://artmmuseum.ru/category/vystavki/tekushhie-vystavki")
    main_page = BeautifulSoup(res.text, "html.parser")

    pagenavi = main_page.find("div", {"class": "wp-pagenavi"})
    page_count = len(pagenavi) - 1  # one child is a left/right navigation arrow

    # starting from the second page, since "main" is the first one
    page_urls = [
        f"https://artmmuseum.ru/category/vystavki/tekushhie-vystavki/page/{i+1}"
        for i in range(1, page_count)
    ]

    # FIXME?: too dense?
    pages = [main_page] + [
        BeautifulSoup(requests.get(url).text, "html.parser") for url in page_urls
    ]

    exhibitions = []
    for page in pages:
        entries = page.find_all("h1", {"class": "h-exibition"})

        # NOTE(anorlovsky): I've seen some <time> entries with just itemprop="datePublished", no start/end date.
        #  but as of 27.09.21 I don't see any such entries - not in the current exhibitions, nor in the archive.
        #  For now I'll keep handling the "datePublished" case.

        # TODO: filter out '<span class="label_archive">' -
        #  sometimes they stay on the "current exhibitions" page for a while
        for entry in entries:
            title = entry.find("a", {"class": "link"})["title"]
            # they prepend "Выставка" to every title attribute, which often leads
            #  to cases like "Выставка Выставка живописи ..."
            title = title.removeprefix("Выставка ")
            # TODO: convert 0xa0 (Windows 1251?) to whitespace

            url = entry.find("a", {"class": "link"})["href"]

            address = parse_address(url) if include_address else None

            # NOTE(anorlovsky): even though the <time> tag has a datetime attribute -
            #  there are some entries with incorrect datetime.
            #  So far I've seen three entries with Unix epoch time as startDate.
            # That's why I parse the user-facing text, not semantic HTML - much more reliable.
            if tag := entry.find("time", {"itemprop": "datePublished"}) is not None:
                start_str = tag.text
                end_str = None
            else:
                start_str = entry.find("time", {"itemprop": "startDate"}).text
                end_str = entry.find("time", {"itemprop": "endDate"}).text

            parse_date = (
                lambda date_str: datetime.strptime(date_str, "%d.%m")
                .replace(year=date.today().year)
                .date()
            )

            start_date = parse_date(start_str)
            if end_str is not None:
                end_date = parse_date(end_str)

            exh = Exhibition(
                title=title,
                url=url,
                start_date=start_date,
                end_date=end_date,
                address=address,
            )
            exhibitions.append(exh)

    return exhibitions

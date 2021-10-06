from datetime import date, datetime
from typing import Optional
from enum import Enum
from dataclasses import dataclass

from pydantic import BaseModel

import requests
import bs4
from bs4 import BeautifulSoup


""" NOTE(anorlovsky)
Rough plan for the project:
- initially - a couple API endpoints (FastAPI) to return the current and future exhibitions of Murmansk Art Museum (https://artmmuseum.ru/)
- eventually (conditional on me staying in Murmansk):
    - build a Telegram bot and a simple website on top of that api
    - extend it with other cultural events (like philharmonia concerts, theater plays, etc.)
    - use rss feeds over web scraping whenever it's possible (run scraping on startup, then schedule RSS-based updates)
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


class TimeLabel(str, Enum):
    NOW = "now"
    SOON = "soon"


class Exhibition(BaseModel):
    title: str
    url: str
    start_date: date
    end_date: date = None
    address: Address = None


def fetch_html(url):
    res = requests.get(url)
    return BeautifulSoup(res.text, "html.parser")


def parse_address(text: str) -> Optional[Address]:
    keywords = {
        Address.MUSEUM: ["коминтерна", "главном здании"],
        Address.PHILHARMONIA: ["перовской", "филарм", "культурно-выставочн"],
        Address.DOMREMESEL: ["книповича"],
    }

    text = text.lower()

    for address, words in keywords.items():
        if any(kw in text for kw in words):
            return address

    return None


# TODO: filter out '<span class="label_archive">' -
#  sometimes they stay on the "current exhibitions" page for a while
def parse_entry(entry: bs4.Tag) -> Optional[Exhibition]:
    """
    The datetime attribute of <time> tags is sometimes incorrect (e.g., Unix epoch time),
      so we scrap the user-facing content.
    """
    if "h-exibition" not in entry["class"]:
        return None

    # I can't use <span itemprop="name">, because it cuts off titles which are too long
    title = entry.find("a", {"class": "link"})["title"]

    # they prepend "Выставка" to every "title" attr, which often leads
    #   to cases like "Выставка Выставка живописи ..."
    title = title.removeprefix("Выставка ")
    # TODO?: convert &nbsp; to regular whitespace?

    url = entry.find("a", {"class": "link"})["href"]

    if (tag := entry.find("time", {"itemprop": "datePublished"})) is not None:
        # the entry is published without an end date
        start = tag.text.removesuffix("Скоро!").removesuffix("Сейчас").strip()
        end = None
    else:
        start = entry.find("time", {"itemprop": "startDate"}).text
        end = entry.find("time", {"itemprop": "endDate"}).text

    # TODO?: perhaps this deserves a separate function (which can also handle None properly)
    parse_date = (
        lambda date_str: datetime.strptime(date_str, "%d.%m")
        .replace(year=date.today().year)
        .date()
    )

    start_date = parse_date(start)
    # FIXME?: not sure if that's a reasonable pattern or an arcane hack, let's ask
    end_date = end and parse_date(end)

    return Exhibition(title=title, url=url, start_date=start_date, end_date=end_date)


def scrap_exhibitions(
    time: TimeLabel, scraped_addrs: dict[str, Address] = {}
) -> list[Exhibition]:
    if time == TimeLabel.NOW:
        url = "https://artmmuseum.ru/category/vystavki/tekushhie-vystavki"
    elif time == TimeLabel.SOON:
        url = "https://artmmuseum.ru/category/vystavki/anons"
    else:
        return None

    pages = [fetch_html(url)]

    if pagenavi := pages[0].find("div", {"class": "wp-pagenavi"}):
        page_count = len(pagenavi) - 1  # one child is a left/right navigation arrow
        # page_count = min(page_count, pages_limit)

        # starting from `/page/2`, since `/page/1` is `pages[0]`
        page_urls = [f"{url}/page/{i+1}" for i in range(1, page_count)]
        pages += [fetch_html(url) for url in page_urls]

    exhibitions = []
    for page in pages:
        entries = page.find_all("h1", {"class": "h-exibition"})
        # entries = entries[:entries_limit]
        exhibitions.extend(parse_entry(x) for x in entries)

    permanent_exhibitions = [
        "https://artmmuseum.ru/vystavka-skulptura-20-21-vekov",
        "https://artmmuseum.ru/otkrylas-postoyannaya-ehkspoziciya",
    ]
    for exh in exhibitions:
        if exh.url in permanent_exhibitions:
            exh.address = Address.MUSEUM
        elif exh.url in scraped_addrs:
            exh.address = scraped_addrs[exh.url]
        else:
            text = fetch_html(exh.url).find("div", {"class": "entry"}).text
            exh.address = parse_address(text)

    return exhibitions

from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime
from enum import Enum
from typing import Iterator, Optional

import bs4
import pydantic
from pydantic.networks import HttpUrl

from ..datatypes import ArtmuseumAddress, ArtmuseumTimeLabel
from ..db.models import ArtmuseumExhibition
from ..scraping.utils import fetch_html


# TODO: handle these two corner cases
# https://artmmuseum.ru/vystavka-iz-cikla-prostye-veshhi-3
# https://artmmuseum.ru/detskaya-galereya-g-apatity-predstavlyaet
#  end date - not sure what the problem is
#  address - we need a regex to catch typos, like r'главном з(\w+)нии Мурманского областного художественного музея'?
def parse_address(text: str) -> Optional[ArtmuseumAddress]:
    keywords = {
        ArtmuseumAddress.MUSEUM: ["коминтерна", "главном здании"],
        ArtmuseumAddress.PHILHARMONIA: ["перовской", "филарм", "культурно-выставочн"],
        ArtmuseumAddress.DOMREMESEL: ["книповича", "народного искусства и рем"],
    }

    text = text.lower()

    for address, words in keywords.items():
        if any(kw in text for kw in words):
            return address

    return None


# TODO: filter out '<span class="label_archive">' -
#  sometimes they stay on the "current exhibitions" page for a while
def parse_entry(entry: bs4.Tag) -> ArtmuseumExhibition:
    if "h-exibition" not in entry["class"]:
        raise ValueError(
            'Provided HTML tag does not match expected format - it has no "h-exibition" attribute.'
        )

    # I can't use <span itemprop="name">, because it cuts off titles which are too long
    title = entry.find("a", {"class": "link"})["title"]

    # they prepend "Выставка" to every "title" attr, which often leads
    #   to cases like "Выставка Выставка живописи ..."
    title = title.removeprefix("Выставка ")
    # TODO: convert &nbsp; to regular whitespace?

    url = entry.find("a", {"class": "link"})["href"]

    # The datetime attribute of <time> tags is sometimes incorrect (e.g., Unix epoch time)
    #   so we parse the user-facing content.
    if (tag := entry.find("time", {"itemprop": "datePublished"})) is not None:
        # the entry is published without an end date
        start = tag.text.removesuffix("Скоро!").removesuffix("Сейчас").strip()
        end = None
    else:
        start = entry.find("time", {"itemprop": "startDate"}).text
        end = entry.find("time", {"itemprop": "endDate"}).text

    # TODO: perhaps this deserves a separate function (which can also handle None properly)
    parse_date = (
        lambda date_str: datetime.strptime(date_str, "%d.%m")
        .replace(year=date.today().year)
        .date()
    )

    start_date = parse_date(start)
    # FIXME: not sure if that's a reasonable pattern or an arcane hack, let's ask
    end_date = end and parse_date(end)

    return ArtmuseumExhibition(
        title=title, url=url, start_date=start_date, end_date=end_date
    )


def scrap_artmuseum(
    known_addrs: dict[HttpUrl, ArtmuseumAddress] = {},
    scrap_addrs: bool = True,
) -> list[ArtmuseumExhibition]:
    urls = [
        "https://artmmuseum.ru/category/vystavki/tekushhie-vystavki",
        "https://artmmuseum.ru/category/vystavki/anons",
    ]
    exhibitions: list[ArtmuseumExhibition] = []

    for url in urls:
        pages = [fetch_html(url)]

        if pagenavi := pages[0].find("div", {"class": "wp-pagenavi"}):
            page_count = len(pagenavi) - 1  # one child is a left/right navigation arrow
            # page_count = min(page_count, pages_limit)

            # starting from `/page/2`, since `/page/1` is `pages[0]`
            page_urls = [f"{url}/page/{i+1}" for i in range(1, page_count)]
            pages += [fetch_html(url) for url in page_urls]

        for page in pages:
            entries = page.find_all("h1", {"class": "h-exibition"})
            # entries = entries[:entries_limit]
            exhibitions.extend(parse_entry(x) for x in entries)

        if scrap_addrs:
            # permanent exhibitions with known address (which is not mentioned on their pages)
            permanent_exhibitions = [
                "https://artmmuseum.ru/vystavka-skulptura-20-21-vekov",
                "https://artmmuseum.ru/otkrylas-postoyannaya-ehkspoziciya",
            ]

            known_addrs |= {
                pydantic.parse_obj_as(HttpUrl, url): ArtmuseumAddress.MUSEUM
                for url in permanent_exhibitions
            }

            unknown_exhs = filter(lambda exh: exh.url not in known_addrs, exhibitions)
            if unknown_exhs:
                unknown_pages: Iterator[bs4.BeautifulSoup]
                with ThreadPoolExecutor(max_workers=20) as executor:
                    unknown_pages = executor.map(
                        fetch_html, [exh.url for exh in unknown_exhs]
                    )

                for exh, page in zip(exhibitions, unknown_pages):
                    text = page.find("div", {"class": "entry"}).text
                    exh.address = parse_address(text)

            for exh in exhibitions:
                # dict.get returns None on non-existent keys.
                exh.address = known_addrs.get(exh.url)  #

    return exhibitions

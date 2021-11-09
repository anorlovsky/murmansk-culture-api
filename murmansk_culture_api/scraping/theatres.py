from datetime import date, datetime
from typing import Optional

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

# from scraping.utils import fetch_html
import utils
from utils import fetch_html


def scrap_teatrsf():
    # NOTE: they post events for a couple of months ahead, and for now I figured only one way
    #  to parse all the events - try parsing pages for consecutive months until you get an "emtpy" page.
    #  Empty pages have the same HTML layout except that the div with event entries is empty.
    #  Also, note that urls can be anything in the form of r`\/afisha\/(\d)+/(\d)+`

    # TODO: scrap all the events (see the note above)
    afisha_url = f"https://teatrsf.ru/afisha/2021/{date.today().month}"
    page = fetch_html(afisha_url)

    plays = []

    for entry in page.find_all("div", {"class": "afisha-perfomance-box"}):
        title_tag = entry.find("div", {"class": "title"}).a
        title = title_tag.text
        url = afisha_url + title_tag["href"]

        info = entry.find("div", {"class": "additional-info"})
        # TODO: xa0 -> '.'
        description = ", ".join(a.text.strip() for a in info.find_all("a"))

        date_tag = entry.find("div", {"class": "date"})
        month, day, time = [
            date_tag.find("div", {"class": div_class})["data-value"]
            for div_class in ("month", "day", "time")
        ]
        date_time = datetime.strptime(time, "%H:%M").replace(
            year=datetime.today().year, month=int(month), day=int(day)
        )

        play = dict(
            title=title,
            url=url,
            description=description,
            datetime=str(date_time),
        )
        plays.append(play)

    return plays


def scrap_modt():
    afisha_url = "https://modt.ru/afisha"
    page = fetch_html(afisha_url)

    # NOTE: this one is a pain to scrap, there's very little semantic HTML/CSS


def scrap_arctictheater():
    page = fetch_html("https://arctictheater.com/calendar")

    for entry in page.find_all("div", {"class": "t778__col"}):
        title = entry.find("div", {"class": "t778__title"}).text

        # NOTE: this one is even messier than modt, no semantics whatsoever


if __name__ == "__main__":
    plays = scrap_teatrsf()
    for play in plays:
        print(play)

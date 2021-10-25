from datetime import datetime

import requests
from bs4 import BeautifulSoup

"""
- https://teatrsf.ru/afisha/2021/10
- https://modt.ru/afisha
- https://arctictheater.com/calendar
"""


def fetch_html(url):
    res = requests.get(url)
    return BeautifulSoup(res.text, "html.parser")


def scrap_teatrsf():
    afisha_url = "https://teatrsf.ru/afisha/2021/10"
    page = fetch_html(afisha_url)

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

        print(play, "\n")


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
    scrap_teatrsf()

from datetime import datetime
from typing import Optional

import bs4

from db.models import PhilharmoniaConcert
from scraping.utils import fetch_html


AFISHA_URL = "https://www.murmansound.ru/afisha"


def parse_entry(entry: bs4.Tag) -> Optional[PhilharmoniaConcert]:
    if entry.name != "li" or "mix" not in entry["class"]:
        return None
    title_tag = entry.find("a", {"class": "mix-title"})
    title = title_tag.text
    url = AFISHA_URL + title_tag["href"]
    description = entry.find("p", {"class": "mix-introtext"}).text

    # TODO: should I avoid using this datetime attribute and rely on user-facing
    #  content instead? (like I did with artmuseum)
    date = datetime.fromisoformat(entry["data-date"]).replace(second=0)

    for_kids = "tag-ДЕТЯМ" in entry["class"]
    pushkin_card = "tag-ПУШКИНСКАЯ-КАРТА" in entry["class"]

    return PhilharmoniaConcert(
        title=title,
        url=url,
        description=description,
        date=date,
        pushkin_card=pushkin_card,
        for_kids=for_kids,
    )


def scrap_philharmonia() -> list[Optional[PhilharmoniaConcert]]:
    page = fetch_html(AFISHA_URL)
    entries = page.find("ul", {"class": "regridart"}).find_all("li", {"class": "mix"})
    return [parse_entry(x) for x in entries]


if __name__ == "__main__":
    print(scrap_philharmonia())

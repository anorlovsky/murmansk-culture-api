from datetime import datetime

from bs4 import BeautifulSoup
import requests


def fetch_html(url):
    res = requests.get(url)
    return BeautifulSoup(res.text, "html.parser")


def scrap_phil():
    afisha_url = "https://www.murmansound.ru/afisha"
    page = fetch_html(afisha_url)

    entries = page.find("ul", {"class": "regridart"})

    # TODO: remove sold-out concerts (or add a flag for that)
    for entry in entries.find_all("li", {"class": "mix"}):
        title_tag = entry.find("a", {"class": "mix-title"})
        title = title_tag.text
        url = afisha_url + title_tag["href"]
        description = entry.find("p", {"class": "mix-introtext"}).text
        # TODO: should I avoid using this datetime attribute and rely on user-facing
        #  content instead? (like I did with artmuseum)
        date = datetime.fromisoformat(entry["data-date"]).replace(second=0)
        for_kids = "tag-ДЕТЯМ" in entry["class"]
        pushkin_card = "tag-ПУШКИНСКАЯ-КАРТА" in entry["class"]

        concert = dict(
            title=title,
            url=url,
            description=description,
            datetime=str(date),
            pushkin_card=pushkin_card,
            for_kids=for_kids,
        )

        print(concert, "\n")


if __name__ == "__main__":
    scrap_phil()

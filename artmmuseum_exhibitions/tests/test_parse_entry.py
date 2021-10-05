from datetime import date
from bs4 import BeautifulSoup

from artmmuseum_exhibitions.scraping import Exhibition, TimeLabel, parse_entry


def html_template(title, url, time_label: TimeLabel, start_date, end_date=None):
    """This template copies the structure of actual data and fills in the values which are used by parsing functions.
    Unused tag attributes are intentionally left blank to improve readability."""
    start = start_date.strftime("%d.%m")
    end = end_date.strftime("%d.%m")

    if time_label == TimeLabel.NOW:
        label_class = "label_now"
        label = "Сейчас"
    elif time_label == TimeLabel.SOON:
        label_class = "label_soon"
        label = "Скоро!"

    label_span = "<span class={label_class}>{label}</span>"

    if end_date is not None:
        date_span = f"""
            с <time itemprop="startDate" datetime="">{start}</time>
            по <time itemprop="endDate" datetime="">{end}</time>
            <br>
            {label_span}"""
    else:
        date_span = f"""
            <time itemprop="datePublished" datetime="2021-10-15">
            {start_date}
            <br>
            {label_span}</time"""

    html = f"""
        <h1 class="h-exibition">
        <a class="link" href={url} title="{"Выставка " + title}" itemprop="url">
          <span itemprop="name">...</span>
        </a>
        <span class="dt_info">
          <span title="">
            {date_span}
           </span>
        </span>
        </h1>"""

    return BeautifulSoup(html, "html.parser").find("h1")


# TODO: more test cases
def test_parse_entry():
    args = {
        "title": "Выставка «Размышления. Поиск. Мастерство»",
        "url": "https://artmmuseum.ru/vystavka-razmyshleniya-poisk-masterstvo",
        "time_label": TimeLabel.NOW,
        "start_date": date(2021, 10, 1),
        "end_date": date(2021, 10, 31),
    }

    entry = html_template(**args)
    assert parse_entry(entry) == Exhibition.parse_obj(args)

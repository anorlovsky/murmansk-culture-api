from datetime import date
from bs4 import BeautifulSoup

from artmmuseum_exhibitions.scraping import Exhibition, TimeLabel, parse_entry


def html_template(
    title="default title",
    url="default url",
    time_label=TimeLabel.NOW,
    start_date=date(2021, 1, 1),
    end_date=None,
):
    """This template copies the structure of actual data and fills in the values which are used by parsing functions.
    Unused tag attributes are intentionally left blank to improve readability."""
    if time_label == TimeLabel.NOW:
        label_class = "label_now"
        label = "Сейчас"
    elif time_label == TimeLabel.SOON:
        label_class = "label_soon"
        label = "Скоро!"

    label_span = f'<span class="{label_class}">{label}</span>'

    if end_date is not None:
        date_span = f"""
            с <time itemprop="startDate" datetime="">{start_date.strftime("%d.%m")}</time>
            по <time itemprop="endDate" datetime="">{end_date.strftime("%d.%m")}</time>
            <br>
            {label_span}"""
    else:
        date_span = f"""
            <time itemprop="datePublished" datetime="2021-10-15">
            {start_date.strftime("%d.%m")}
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


def test_parse_title():
    title = "Выставка «Размышления. Поиск. Мастерство»"
    entry = html_template(title=title)

    assert parse_entry(entry).title == title


def test_parse_url():
    url = "https://artmmuseum.ru/vystavka-razmyshleniya-poisk-masterstvo"
    entry = html_template(url=url)

    assert parse_entry(entry).url == url


def test_parse_dates():
    start_date = date(2021, 10, 1)
    end_date = date(2021, 10, 31)

    entry_now = html_template(
        time_label=TimeLabel.NOW, start_date=start_date, end_date=end_date
    )
    entry_soon = html_template(
        time_label=TimeLabel.SOON, start_date=start_date, end_date=end_date
    )

    for entry in [entry_now, entry_soon]:
        exh = parse_entry(entry)
        assert exh.start_date == start_date
        assert exh.end_date == end_date


def test_parse_without_end_date():
    start_date = date(2021, 10, 10)

    entry_now = html_template(time_label=TimeLabel.NOW, start_date=start_date)
    entry_soon = html_template(time_label=TimeLabel.SOON, start_date=start_date)

    for entry in [entry_now, entry_soon]:
        exh = parse_entry(entry)
        assert exh.start_date == start_date


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

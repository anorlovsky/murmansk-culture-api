import requests
from bs4 import BeautifulSoup


def fetch_html(url: str):
    res = requests.get(url)
    return BeautifulSoup(res.text, "html.parser")

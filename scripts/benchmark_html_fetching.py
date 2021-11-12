from concurrent.futures import ThreadPoolExecutor
from functools import partial, wraps
from inspect import getcallargs
from timeit import timeit

from murmansk_culture_api.scraping.utils import fetch_html


def timer(func):
    @wraps(func)
    def wrapper(*args):
        time = timeit(partial(func, *args), number=1)
        callargs = getcallargs(func, *args)
        callargs_str = ", ".join(f"{k}={v}" for k, v in callargs.items())
        print(f"{func.__name__} ({callargs_str}): {round(time, 1)} seconds")

    return wrapper


# list based on https://gist.github.com/ekapujiw2002/23ca18cecdacce4f3594ecf8cfc5744c
urls = [
    "https://www.youtube.com",
    "https://www.amazon.com",
    "https://www.wikipedia.org",
    "https://www.twitter.com",
    "https://www.reddit.com",
    "https://www.pinterest.com",
    "https://www.wordpress.com",
    "https://www.tumblr.com",
    "https://www.blogspot.com",
    "https://www.imgur.com",
    "https://www.stackoverflow.com",
    "https://www.apple.com",
    "https://www.github.com",
    "https://www.imdb.com",
    "https://www.dropbox.com",
    "https://www.twitch.tv",
    "https://www.accuweather.com",
    "https://news.ycombinator.com/",
    "https://archlinux.org/",
]


@timer
def sequential_fetching():
    for url in urls:
        fetch_html(url)


@timer
def threadpool_executor(num_workers=20):
    with ThreadPoolExecutor(num_workers) as executor:
        executor.map(fetch_html, urls)


if __name__ == "__main__":
    sequential_fetching()
    threadpool_executor(5)
    threadpool_executor(len(urls) // 2)
    threadpool_executor(len(urls))

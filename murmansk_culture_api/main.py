import asyncio

import uvicorn
from fastapi import FastAPI, Query

from model import Data
from scraping.artmuseum import Exhibition, TimeLabel
from scraping.philharmonia import PhilharmoniaConcert

# TODO: move under __name__ == '__main__'?
data = Data()
app = FastAPI(
    title="Murmansk Culture API",
    # description="",
    version="0.0.1",
    contact={
        "name": "Arthur Orlovsky",
        "url": "https://github.com/anorlovsky",
        "email": "orlovsky.arthur@gmail.com",
    },
    redoc_url="/",
    docs_url=None,
)


@app.on_event("startup")
def init_data():
    # initting here because it uses uvicorn logger
    data.init()
    # TODO: first update should be based on the last one
    asyncio.create_task(data.loop_scraping())


@app.get(
    "/artmuseum",
    response_model=list[Exhibition],
    description="Возвращает список текущих и ближайших выставок [Мурманского областного художественного музея](https://artmmuseum.ru/)",
)
async def get_artmuseum_exhibitions(
    time: TimeLabel = Query(
        None,
        description='Вернуть только текущие (`"now"`) или только ближайшие (`"soon"`) выставки',
    )
):
    if time is None:
        return data.current_exhibitions + data.upcoming_exhibitions
    if time == TimeLabel.NOW:
        return data.current_exhibitions
    if time == TimeLabel.SOON:
        return data.upcoming_exhibitions


@app.get(
    "/philharmonia",
    response_model=list[PhilharmoniaConcert],
    description="Возвращает список ближайших концертов [Мурманской областной филармонии](https://www.murmansound.ru)",
)
async def get_philharmonia_concerts():
    return data.concerts


# TODO: pass kwargs for uvicorn.run through main.py
#  (to enable either proxying with --root_path or --reload)
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        log_config="log_config.yaml",
        proxy_headers=True,
        forwarded_allow_ips="*",
        root_path="",
    )

import asyncio

import uvicorn
from fastapi import FastAPI

from model import Data
from scraping.artmuseum import Exhibition, TimeLabel
from scraping.philharmonia import PhilharmoniaConcert

# TODO: move under __name__ == '__main__'?
data = Data()
app = FastAPI(redoc_url="/", docs_url=None)


@app.on_event("startup")
def init_data():
    # initting here because it uses uvicorn logger
    data.init()
    # TODO: first update should be based on the last one
    asyncio.create_task(data.loop_scraping())


@app.get("/artmuseum", response_model=list[Exhibition])
async def serve_exhibitions(time: TimeLabel = None):
    if time is None:
        return data.current_exhibitions + data.upcoming_exhibitions
    if time == TimeLabel.NOW:
        return data.current_exhibitions
    if time == TimeLabel.SOON:
        return data.upcoming_exhibitions


@app.get("/philharmonia", response_model=list[PhilharmoniaConcert])
async def serve_concerts():
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

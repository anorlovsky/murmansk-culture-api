import asyncio
import logging

import uvicorn
from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse

from model import Data
from scraping.artmuseum import Exhibition, TimeLabel

# TODO: move under __name__ == '__main__'?
data = Data()
app = FastAPI(redoc_url="/api/docs", docs_url=None)


@app.on_event("startup")
def init_data():
    # initting here because it uses uvicorn logger
    data.init()
    # TODO: first update should be based on the last one
    asyncio.create_task(data.loop_scraping())


@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse("https://github.com/anorlovsky/artmuseum")


@app.get("/api", response_model=list[Exhibition])
async def serve_exhibitions(time: TimeLabel = None):
    if time is None:
        return data.current_exhibitions + data.upcoming_exhibitions
    if time == TimeLabel.NOW:
        return data.current_exhibitions
    if time == TimeLabel.SOON:
        return data.upcoming_exhibitions


# @app.get("/api/artmuseum", response_model=list[ArtmuseumExhibition])
# async def serve_artmuseum(time: TimeLabel = None):
#     if time is None:
#         return data.current + data.upcoming
#     if time == TimeLabel.NOW:
#         return data.current
#     if time == TimeLabel.SOON:
#         return data.upcoming


# @app.get("/api/philharmonia", response_model=list[PhilharmoniaConcert])
# async def serve_philharmsonia():


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

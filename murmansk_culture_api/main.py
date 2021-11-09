from fastapi import FastAPI, Query
from sqlmodel import Session, create_engine, select

from db.crud import init_db
from db.models import PhilharmoniaConcert
from scraping.artmuseum import Exhibition, TimeLabel


sql_engine = create_engine(
    "sqlite:///database.db", connect_args={"check_same_thread": False}
)
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
def on_startup():
    init_db(sql_engine)


# @app.get(
#     "/artmuseum",
#     response_model=list[Exhibition],
#     description="Возвращает список текущих и ближайших выставок [Мурманского областного художественного музея](https://artmmuseum.ru/)",
# )
# async def get_artmuseum_exhibitions(
#     time: TimeLabel = Query(
#         None,
#         description='Вернуть только текущие (`"now"`) или только ближайшие (`"soon"`) выставки',
#     )
# ):
#     if time is None:
#         return data.current_exhibitions + data.upcoming_exhibitions
#     if time == TimeLabel.NOW:
#         return data.current_exhibitions
#     if time == TimeLabel.SOON:
#         return data.upcoming_exhibitions


@app.get(
    "/philharmonia",
    response_model=list[PhilharmoniaConcert],
    description="Возвращает список ближайших концертов [Мурманской областной филармонии](https://www.murmansound.ru)",
)
async def get_philharmonia_concerts():
    with Session(sql_engine) as session:
        concerts = session.exec(select(PhilharmoniaConcert)).all()
        return concerts


if __name__ == "__main__":
    # for development only, see deployment/README.md on running the app in production.
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        log_config="log_config.yaml",
        reload=True,
    )

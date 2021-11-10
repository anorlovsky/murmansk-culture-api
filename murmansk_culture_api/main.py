from fastapi import FastAPI, Query
from sqlmodel import Session, create_engine, select

from .datatypes import ArtmuseumAddress, ArtmuseumTimeLabel
from .db.crud import init_db
from .db.models import ArtmuseumExhibition, PhilharmoniaConcert


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


@app.get(
    "/artmuseum",
    response_model=list[ArtmuseumExhibition],
    description="Возвращает список текущих и ближайших выставок [Мурманского областного художественного музея](https://artmmuseum.ru/)",
)
async def get_artmuseum_exhibitions(
    time: ArtmuseumTimeLabel = Query(
        None,
        description='Вернуть только текущие (`"now"`) или только ближайшие (`"soon"`) выставки',
    )
):
    concerts: list[ArtmuseumExhibition]
    with Session(sql_engine) as session:
        if time is None:
            concerts = session.exec(select(ArtmuseumExhibition)).all()

        return concerts

    # if time == ArtmuseumTimeLabel.NOW:
    #     return data.current_exhibitions
    # if time == ArtmuseumTimeLabel.SOON:
    #     return data.upcoming_exhibitions


@app.get(
    "/philharmonia",
    response_model=list[PhilharmoniaConcert],
    description="Возвращает список ближайших концертов [Мурманской областной филармонии](https://www.murmansound.ru)",
)
async def get_philharmonia_concerts():
    with Session(sql_engine) as session:
        concerts = session.exec(select(PhilharmoniaConcert)).all()
        return concerts

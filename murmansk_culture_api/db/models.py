from datetime import date, datetime
from typing import Optional

from pydantic import HttpUrl
from sqlmodel import Field, SQLModel

from ..datatypes import ArtmuseumAddress, ArtmuseumTimeLabel


class PhilharmoniaConcert(SQLModel, table=True):
    title: str
    url: HttpUrl = Field(..., primary_key=True)
    description: str
    date: datetime
    pushkin_card: bool = Field(
        ...,
        description="Возможность оплатить билет [Пушкинской картой](https://www.culture.ru/pushkinskaya-karta)",
    )
    for_kids: bool = Field(..., description="Предназначенные для детей концерты")


class ArtmuseumExhibition(SQLModel, table=True):
    title: str
    url: HttpUrl = Field(..., primary_key=True)
    start_date: date
    end_date: Optional[date] = None
    address: Optional[ArtmuseumAddress] = None

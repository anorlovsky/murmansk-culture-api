from datetime import date, datetime
from typing import Optional

from pydantic import HttpUrl
from sqlmodel import Field, SQLModel

from ..datatypes import ArtmuseumAddress, ArtmuseumTimeLabel


# TODO: exclude id's from pydantic models (let's do it here, not in the fastapi routing code)
class PhilharmoniaConcert(SQLModel, table=True):
    # __tablename__ = "..."
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    url: HttpUrl
    description: str
    date: datetime
    pushkin_card: bool = Field(
        ...,
        description="Возможность оплатить билет [Пушкинской картой](https://www.culture.ru/pushkinskaya-karta)",
    )
    for_kids: bool = Field(..., description="Предназначенные для детей концерты")


class ArtmuseumExhibition(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    url: HttpUrl
    start_date: date
    end_date: Optional[date] = None
    address: Optional[ArtmuseumAddress] = None

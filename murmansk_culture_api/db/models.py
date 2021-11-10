from datetime import date, datetime
from typing import Optional

from sqlmodel import Field, SQLModel

from ..datatypes import ArtmuseumAddress, ArtmuseumTimeLabel


# TODO: use pydantic's "URL" type
class PhilharmoniaConcert(SQLModel, table=True):
    # __tablename__ = "..."
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    url: str
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
    url: str
    start_date: date
    end_date: Optional[date] = None
    address: Optional[ArtmuseumAddress] = None

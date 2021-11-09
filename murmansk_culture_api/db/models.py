from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class PhilharmoniaConcert(SQLModel, table=True):
    # __tablename__ = "phil_concerts"
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

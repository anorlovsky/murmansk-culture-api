from enum import Enum


class ArtmuseumAddress(str, Enum):
    MUSEUM = "Мурманский областной художественный музей (ул. Коминтерна, д.13)"
    PHILHARMONIA = (
        "Культурно-выставочный центр Русского музея (Мурманская областная филармония"
        " - ул. Софьи Перовской, д. 3, второй этаж)"
    )
    DOMREMESEL = (
        "Отдел народного искусства и ремёсел (Дом Ремёсел - ул. Книповича, д. 23А)"
    )


class ArtmuseumTimeLabel(str, Enum):
    NOW = "now"
    SOON = "soon"

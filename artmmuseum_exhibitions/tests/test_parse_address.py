from artmmuseum_exhibitions.scraping import Address, parse_address


def test_address_museum():
    cases = [
        "в Мурманском областном художественном музее (Коминтерна, д.13)",
        "В главном здании Мурманского областного художественного музея",
        "по адресу: ул. Коминтерна, д.13, 2 этаж.",
    ]

    for case in cases:
        assert parse_address(case) == Address.MUSEUM


def test_address_phil():
    cases = [
        "в отделе музея «Культурно-выставочный центр Русского музея»",
        "С. Перовской, д.3, 2 этаж",
        "здание филармонии, 2 этаж",
        "ул. Софьи Перовской, д. 3, второй этаж",
    ]

    for case in cases:
        assert parse_address(case) == Address.PHILHARMONIA


def test_address_domremesel():
    cases = [
        "отдел народного искусства и ремесел",
        "в отделе народного искусства и ремёсел",
        "ул. Книповича, д. 23а",
    ]

    for case in cases:
        assert parse_address(case) == Address.DOMREMESEL

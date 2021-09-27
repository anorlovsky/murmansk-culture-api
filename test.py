from parse import *


def test_parse_address():
    addrs = {
        Address.MUSEUM: [
            "https://artmmuseum.ru/vystavka-po-volnam-moejj-pamyati",
            "https://artmmuseum.ru/umnaya-gostinaya-umnyjj-muzejj",
            "https://artmmuseum.ru/vystavka-grafika-vladimira-borisovicha-chernova",
            "https://artmmuseum.ru/vystavka-batik-bez-granic",
        ],
        Address.PHILHARMONIA: [
            "https://artmmuseum.ru/k-k-85-letiyu-so-dnya-rozhdeniya-khudozhnika-vadima-konstantinovicha-koneva",
            "https://artmmuseum.ru/vystavka-russkijj-farfor-khkh-veka-iz-sobraniya-muzeya-i-chastnykh-kollekcijj",
            "https://artmmuseum.ru/khudozhestvennyjj-promysly-rossii-chast-1-iz-sobraniya-muzeya",
            "https://artmmuseum.ru/vystavka-medicina-severnykh-rubezhejj",
            "https://artmmuseum.ru/vystavka-dyagilev-i-ego-okruzhenie",
        ],
        Address.DOMREMESEL: [
            "https://artmmuseum.ru/oblastnaya-vystavka-tkachestva-dorogi-paraskevy"
        ],
        Address.UNKNOWN: [
            "https://artmmuseum.ru/otkrylas-postoyannaya-ehkspoziciya",
        ],
    }

    # for addr, urls in addrs.items():
    #     for url in urls:
    #         assert parse_address(url) == addr

    try:
        for addr, urls in addrs.items():
            for url in urls:
                assert parse_address(url) == addr
    except AssertionError as err:
        print(addr, url)


if __name__ == "__main__":
    # test_parse_address()

    exhibitions = scrap_current_exhibitions(include_address=False)

    for exh in exhibitions:
        print(exh, "\n")

from scrap import *

'''
TODO: 
- use static (offline) test data for testing the parsing methods
- for testing the actual web scraping we just call the scrap_exhibitions function, making sure it works and Pydantic validates the data
    - no need to check the content of scrapped stuff, because parsing is tested by other tests with static test data

- testing parse_entry
  - download some HTML pages from the artmmuseum website, strip out scripts
  - write your own HTML entries with edge cases, using their template (perhaps make a function for generating them)   
'''

# def test_parse_address():
#     addrs = {
#         Address.MUSEUM: [
#             "https://artmmuseum.ru/vystavka-po-volnam-moejj-pamyati",
#             "https://artmmuseum.ru/umnaya-gostinaya-umnyjj-muzejj",
#             "https://artmmuseum.ru/vystavka-grafika-vladimira-borisovicha-chernova",
#             "https://artmmuseum.ru/vystavka-batik-bez-granic",
#         ],
#         Address.PHILHARMONIA: [
#             "https://artmmuseum.ru/k-k-85-letiyu-so-dnya-rozhdeniya-khudozhnika-vadima-konstantinovicha-koneva",
#             "https://artmmuseum.ru/vystavka-russkijj-farfor-khkh-veka-iz-sobraniya-muzeya-i-chastnykh-kollekcijj",
#             "https://artmmuseum.ru/khudozhestvennyjj-promysly-rossii-chast-1-iz-sobraniya-muzeya",
#             "https://artmmuseum.ru/vystavka-medicina-severnykh-rubezhejj",
#             "https://artmmuseum.ru/vystavka-dyagilev-i-ego-okruzhenie",
#         ],
#         Address.DOMREMESEL: [
#             "https://artmmuseum.ru/oblastnaya-vystavka-tkachestva-dorogi-paraskevy"
#         ],
#         None: [
#             "https://artmmuseum.ru/otkrylas-postoyannaya-ehkspoziciya",
#         ],
#     }

#     try:
#         for addr, urls in addrs.items():
#             for url in urls:
#                 assert scrap_address(url) == addr
#     except AssertionError as err:
#         print(addr, url)


if __name__ == "__main__":
    # test_parse_address()

    # exhibitions = ...
    # with open("exhibitions.pickle", "wb") as file:
    #     pickle.dump(exhibitions, file)

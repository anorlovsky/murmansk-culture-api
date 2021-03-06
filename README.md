# murmansk-culture-api

[![Test](https://github.com/anorlovsky/murmansk-culture-api/actions/workflows/test.yml/badge.svg)](https://github.com/anorlovsky/murmansk-culture-api/actions/workflows/test.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

**Disclaimer**: this project is mostly on hiatus since I started working. I might occasionally play around with some interesting work-related tech, but there's no plan to add API features or work on the Telegram client any time soon.

**API**: http://anorlovsky.me/murmansk-culture/api/

## О проекте
В этом API представлена афиша избранных мной мероприятий культурной и интеллектуальной жизни Мурманска.  
Информация о мероприятих собирается автоматически с официальных сайтов.

### Список мероприятий на данный момент

| Мероприятие 	| API endpoint 	| Документация 	|
|:---:	|:---:	|:---:	|
| выставки  [Мурманского областного художественного музея](https://artmmuseum.ru/) 	| [/artmuseum](https://anorlovsky.me/murmansk-culture/api/artmuseum) 	| [URL](https://anorlovsky.me/murmansk-culture/api/#operation/get_artmuseum_exhibitions_artmuseum_get) 	|
| концерты [Мурманской областной филармонии](https://www.murmansound.ru/) 	| [/philharmonia](https://anorlovsky.me/murmansk-culture/api/philharmonia) 	| [URL](https://anorlovsky.me/murmansk-culture/api/#operation/get_philharmonia_concerts_philharmonia_get) 	|

## Дальнейшие планы
- расширить API информацией о других культурных мероприятиях города  
- создать Telegram-бота и вебсайт на основе API

# Development
This section is about developing in a local dev environment. For production environment see the [deployment guide](deployment/README.md).

## Requirements
- Python 3.9+

## Setting up your dev environment
```shell
$ git clone https://github.com/anorlovsky/murmansk-culture-api.git
$ cd murmansk-culture-api
$ python -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
```
## Running tests
Testing is done with **pytest**

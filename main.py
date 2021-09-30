import pickle
from fastapi import FastAPI
from parse import Exhibition

app = FastAPI()


""" TODO:
on startup:
  - check if there is an up-to-date pickle file with all the data
    - yes - load it
    - no - scrap the data, pickle.dump it
  - schedule data scraping (every 6/12 hours?)
"""

# TODO: schedule periodic async scraping and serialization of data


with open("exhibitions.pickle", "rb") as file:
    exhibitions = pickle.load(file)


@app.get("/now", response_model=list[Exhibition])
async def current_exhibitions():
    return exhibitions

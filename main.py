import json
from fastapi import FastAPI
from parse import Exhibition, scrap_current_exhibitions

app = FastAPI()


""" TODO:
on startup:
  - check if there is an up-to-date json file with all the data
    - yes - load it
    - no - scrap the data, save as json
  - schedule data scrapping (every 6/12 hours?)
"""

# with open("exhibitions.json", "r") as file:

exhibitions = scrap_current_exhibitions()


@app.get("/now", response_model=list[Exhibition])
async def current_exhibitions():
    return exhibitions

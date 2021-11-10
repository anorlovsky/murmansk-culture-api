"""This script is used for interactively connecting to the database with ipython: 
  `ipython -i scripts/db-connect.py`"""
import logging

from sqlmodel import Session, create_engine, select

from murmansk_culture_api.db.crud import refresh_data
from murmansk_culture_api.db.models import ArtmuseumExhibition


logging.getLogger().setLevel(logging.INFO)

engine = create_engine(
    "sqlite:///database.db", connect_args={"check_same_thread": False}
)

session = Session(engine)

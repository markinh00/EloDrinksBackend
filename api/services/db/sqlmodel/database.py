import os
from dotenv import load_dotenv
from sqlmodel import create_engine, Session

load_dotenv()

POSTGRES_URI = os.getenv("POSTGRES_URI")

engine = create_engine(POSTGRES_URI, echo=True)

def get_session():
    return Session(engine)
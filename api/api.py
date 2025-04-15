from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import bar_structure

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(bar_structure.router)


@app.get("/")
def read_root():
    return

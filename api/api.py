from fastapi import FastAPI

from api.routes import bar_structure

app = FastAPI()

app.include_router(bar_structure.router)


@app.get("/")
def read_root():
    return

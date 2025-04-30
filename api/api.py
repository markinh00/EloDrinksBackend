from fastapi import FastAPI, Security
from api.dependencies.auth import get_api_key
from api.routes.auth import register, login
from api.routes import bar_structure, customer, product, pack, sale
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(dependencies=[Security(get_api_key)])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(register.router)
app.include_router(login.router)
app.include_router(customer.router)
app.include_router(bar_structure.router)
app.include_router(product.router)
app.include_router(pack.router)
app.include_router(sale.router)

@app.get("/")
def read_root():
    return

from fastapi import FastAPI, Security
from api.dependencies.auth import get_api_key
from api.routes.auth import register, login, me
from api.routes import bar_structure, customer, order, product, pack, sale, notification
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
app.include_router(me.router)
app.include_router(customer.router)
app.include_router(bar_structure.router)
app.include_router(product.router)
app.include_router(pack.router)
app.include_router(sale.router)
app.include_router(order.router)
app.include_router(notification.router)


@app.get("/")
def read_root():
    return

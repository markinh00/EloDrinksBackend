from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

from api.schemas.order import OrderCreate, OrderInDB
from api.services.db.mongodb.mongo_connection import (
    connect_mongo,
)

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderInDB, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: OrderCreate,
    collection: AsyncIOMotorCollection = Depends(connect_mongo),
):
    now = datetime.now()

    order_dict = order.model_dump()
    order_dict["created_at"] = now
    order_dict["updated_at"] = now

    result = await collection.insert_one(order_dict)
    order_in_db = collection.find_one({"_id": result.inserted_id})
    return order_in_db

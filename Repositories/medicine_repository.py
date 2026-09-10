from datetime import date, datetime, time, timezone
from typing import Optional

from bson import ObjectId
from bson.decimal128 import Decimal128
from pymongo.asynchronous.collection import AsyncCollection


class MedicineRepository:
    def __init__(self, collection: AsyncCollection):
        self.collection = collection

    async def create(self, medicine_data: dict) -> dict:

        medicine_data = medicine_data.copy()

        # Convert Python Decimal to MongoDB Decimal128
        if "price" in medicine_data:
            medicine_data["price"] = Decimal128(
                medicine_data["price"]
            )

        # Convert Python date to MongoDB datetime
        if (
            "expiry" in medicine_data
            and medicine_data["expiry"] is not None
        ):
            medicine_data["expiry"] = datetime.combine(
                medicine_data["expiry"],
                time.min,
                tzinfo=timezone.utc,
            )

        result = await self.collection.insert_one(medicine_data)

        created_medicine = await self.collection.find_one(
            {"_id": result.inserted_id}
        )

        if created_medicine is None:
            raise RuntimeError(
                "Medicine was created but could not be retrieved"
            )

        return created_medicine

    async def get_by_id(
        self,
        medicine_id: ObjectId,
    ) -> Optional[dict]:

        return await self.collection.find_one(
            {"_id": medicine_id}
        )

    async def get_all(self) -> list[dict]:

        cursor = self.collection.find()

        return await cursor.to_list()

    async def get_by_name(
        self,
        name: str,
    ) -> Optional[dict]:

        return await self.collection.find_one(
            {"name": name}
        )

    async def search(
        self,
        query: str,
    ) -> list[dict]:

        cursor = self.collection.find({
            "name": {
                "$regex": query,
                "$options": "i",
            }
        })

        return await cursor.to_list()

    async def update(
        self,
        medicine_id: ObjectId,
        update_data: dict,
    ) -> Optional[dict]:

        update_data = update_data.copy()

        # Convert Python Decimal to MongoDB Decimal128
        if "price" in update_data:
            update_data["price"] = Decimal128(
                update_data["price"]
            )

        # Convert Python date to MongoDB datetime
        if ("expiry" in update_data and update_data["expiry"] is not None):
            update_data["expiry"] = datetime.combine(
                update_data["expiry"],
                time.min,
                tzinfo=timezone.utc,
            )

        result = await self.collection.update_one(
            {"_id": medicine_id},
            {"$set": update_data},
        )

        if result.matched_count == 0:
            return None

        return await self.collection.find_one(
            {"_id": medicine_id}
        )

    async def delete(
        self,
        medicine_id: ObjectId,
    ) -> bool:

        result = await self.collection.delete_one(
            {"_id": medicine_id}
        )

        return result.deleted_count > 0
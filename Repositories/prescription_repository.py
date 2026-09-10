from typing import Optional

from bson import ObjectId
from pymongo.asynchronous.collection import AsyncCollection


class PrescriptionRepository:

    def __init__(self, collection: AsyncCollection):
        self.collection = collection

    async def create(self, prescription_data: dict) -> dict:
        prescription_data = prescription_data.copy()

        result = await self.collection.insert_one(
            prescription_data
        )

        created_prescription = await self.collection.find_one(
            {"_id": result.inserted_id}
        )

        if created_prescription is None:
            raise RuntimeError(
                "Prescription was created but could not be retrieved"
            )

        return created_prescription

    async def get_by_id(
        self,
        prescription_id: ObjectId,
    ) -> Optional[dict]:

        return await self.collection.find_one(
            {"_id": prescription_id}
        )

    async def get_all(self) -> list[dict]:

        cursor = self.collection.find()

        return await cursor.to_list()

    async def update(
        self,
        prescription_id: ObjectId,
        update_data: dict,
    ) -> Optional[dict]:

        update_data = update_data.copy()

        result = await self.collection.update_one(
            {"_id": prescription_id},
            {"$set": update_data},
        )

        if result.matched_count == 0:
            return None

        return await self.collection.find_one(
            {"_id": prescription_id}
        )

    async def delete(
        self,
        prescription_id: ObjectId,
    ) -> bool:

        result = await self.collection.delete_one(
            {"_id": prescription_id}
        )

        return result.deleted_count > 0
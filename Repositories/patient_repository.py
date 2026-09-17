from typing import Optional

from bson import ObjectId
from pymongo.asynchronous.collection import AsyncCollection


class PatientRepository:

    def __init__(self, collection: AsyncCollection):
        self.collection = collection

    async def create(self, patient_data: dict) -> dict:
        patient_data = patient_data.copy()

        result = await self.collection.insert_one(
            patient_data
        )

        created_patient = await self.collection.find_one(
            {"_id": result.inserted_id}
        )

        if created_patient is None:
            raise RuntimeError(
                "Patient was created but could not be retrieved"
            )

        return created_patient

    async def get_by_id(
        self,
        patient_id: ObjectId,
    ) -> Optional[dict]:

        return await self.collection.find_one(
            {"_id": patient_id}
        )

    async def get_all(self) -> list[dict]:

        cursor = self.collection.find()

        return await cursor.to_list()

    async def update(
        self,
        patient_id: ObjectId,
        update_data: dict,
    ) -> Optional[dict]:

        update_data = update_data.copy()

        result = await self.collection.update_one(
            {"_id": patient_id},
            {"$set": update_data},
        )

        if result.matched_count == 0:
            return None

        return await self.collection.find_one(
            {"_id": patient_id}
        )

    async def delete(
        self,
        patient_id: ObjectId,
    ) -> bool:

        result = await self.collection.delete_one(
            {"_id": patient_id}
        )

        return result.deleted_count > 0

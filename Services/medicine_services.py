from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId

from MongoDB.schemas import CreateMedicine, ReadMedicine, UpdateMedicine
from Repositories.medicine_repository import MedicineRepository
from exceptions.medicine import (
    EmptyMedicineUpdateError,
    InvalidMedicineIdError,
    MedicineNotFoundError,
)


class MedicineService:

    def __init__(self, repository: MedicineRepository):
        self.repository = repository

    @staticmethod
    def _to_read_schema(medicine: dict) -> ReadMedicine:
        return ReadMedicine(
            id=str(medicine["_id"]),
            name=medicine.get("name", ""),
            quantity=medicine.get("quantity", 0),
            price=medicine.get("price"),
            expiry=medicine.get("expiry"),
            created_at=medicine.get("created_at"),
            updated_at=medicine.get("updated_at"),
        )

    @staticmethod
    def _parse_object_id(medicine_id: str) -> ObjectId:
        try:
            return ObjectId(medicine_id)
        except InvalidId:
            raise InvalidMedicineIdError(medicine_id)

    def list_medicines(self) -> list[ReadMedicine]:
        medicines = self.repository.get_all()

        return [
            self._to_read_schema(medicine)
            for medicine in medicines
        ]

    def get_medicine(self, medicine_id: str) -> ReadMedicine:
        object_id = self._parse_object_id(medicine_id)

        medicine = self.repository.get_by_id(object_id)

        if medicine is None:
            raise MedicineNotFoundError(medicine_id)

        return self._to_read_schema(medicine)

    def create_medicine(
        self,
        data: CreateMedicine,
    ) -> ReadMedicine:

        medicine_data = data.model_dump()

        now = datetime.now(timezone.utc)

        medicine_data["created_at"] = now
        medicine_data["updated_at"] = now

        medicine = self.repository.create(medicine_data)

        return self._to_read_schema(medicine)

    def update_medicine(
        self,
        medicine_id: str,
        data: UpdateMedicine,
    ) -> ReadMedicine:

        object_id = self._parse_object_id(medicine_id)

        update_data = data.model_dump(
            exclude_unset=True
        )

        if not update_data:
            raise EmptyMedicineUpdateError()

        update_data["updated_at"] = datetime.now(timezone.utc)

        medicine = self.repository.update(
            object_id,
            update_data,
        )

        if medicine is None:
            raise MedicineNotFoundError(medicine_id)

        return self._to_read_schema(medicine)

    def delete_medicine(
        self,
        medicine_id: str,
    ) -> None:

        object_id = self._parse_object_id(medicine_id)

        deleted = self.repository.delete(object_id)

        if not deleted:
            raise MedicineNotFoundError(medicine_id)

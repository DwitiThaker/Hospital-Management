from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId

from DB.schemas import (
    CreatePrescription,
    ReadPrescription,
    UpdatePrescription,
    PrescriptionMedicine,
)
from Repositories.prescription_repository import PrescriptionRepository

from exceptions.prescription import (
    EmptyPrescriptionUpdateError,
    InvalidPrescriptionIdError,
    PrescriptionNotFoundError,
)


class PrescriptionService:

    def __init__(self, repository: PrescriptionRepository):
        self.repository = repository

    @staticmethod
    def _to_read_schema(prescription: dict) -> ReadPrescription:
        return ReadPrescription(
            prescription_id=str(prescription["_id"]),
            doctor_id=str(prescription["doctor_id"]),
            patient_id=prescription["patient_id"],
            patient_name=prescription["patient_name"],
            description=prescription["description"],
            medicines=[
                PrescriptionMedicine(
                    medicine_id=str(medicine["medicine_id"]),
                    quantity=medicine["quantity"],
                )
                for medicine in prescription.get("medicines", [])
            ],
            duration_days=prescription["duration_days"],
            issued_at=prescription["issued_at"],
            updated_at=prescription["updated_at"],
        )

    @staticmethod
    def _parse_object_id(prescription_id: str) -> ObjectId:
        try:
            return ObjectId(prescription_id)
        except InvalidId:
            raise InvalidPrescriptionIdError(prescription_id)

    async def list_prescriptions(self) -> list[ReadPrescription]:
        prescriptions = await self.repository.get_all()

        return [self._to_read_schema(prescription) for prescription in prescriptions]

    async def get_prescription(self, prescription_id: str) -> ReadPrescription:
        object_id = self._parse_object_id(prescription_id)

        prescription = await self.repository.get_by_id(object_id)

        if prescription is None:
            raise PrescriptionNotFoundError(prescription_id)

        return self._to_read_schema(prescription)

    async def create_prescription(
        self,
        data: CreatePrescription,
        doctor_id: str,
    ) -> ReadPrescription:

        prescription_data = data.model_dump()

        # Convert doctor ID from API string to MongoDB ObjectId
        try:
            doctor_object_id = ObjectId(doctor_id)
        except InvalidId:
            raise ValueError("Invalid doctor ID")

        prescription_data["doctor_id"] = doctor_object_id

        # Convert medicine IDs from API strings to MongoDB ObjectIds
        for medicine in prescription_data["medicines"]:
            try:
                medicine["medicine_id"] = ObjectId(medicine["medicine_id"])
            except InvalidId:
                raise ValueError(f"Invalid medicine ID: {medicine['medicine_id']}")

        now = datetime.now(timezone.utc)

        prescription_data["created_at"] = now
        prescription_data["updated_at"] = now
        prescription_data["issued_at"] = now

        prescription = await self.repository.create(prescription_data)

        return self._to_read_schema(prescription)

    async def update_prescription(
        self,
        prescription_id: str,
        data: UpdatePrescription,
    ) -> ReadPrescription:

        object_id = self._parse_object_id(prescription_id)

        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            raise EmptyPrescriptionUpdateError()

        # Convert medicine IDs from strings to MongoDB ObjectIds
        if "medicines" in update_data:
            for medicine in update_data["medicines"]:
                try:
                    medicine["medicine_id"] = ObjectId(medicine["medicine_id"])
                except InvalidId:
                    raise ValueError(f"Invalid medicine ID: {medicine['medicine_id']}")

        update_data["updated_at"] = datetime.now(timezone.utc)

        prescription = await self.repository.update(
            object_id,
            update_data,
        )

        if prescription is None:
            raise PrescriptionNotFoundError(prescription_id)

        return self._to_read_schema(prescription)

    async def delete_prescription(
        self,
        prescription_id: str,
    ) -> None:

        object_id = self._parse_object_id(prescription_id)

        deleted = await self.repository.delete(object_id)

        if not deleted:
            raise PrescriptionNotFoundError(prescription_id)

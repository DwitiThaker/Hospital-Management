from datetime import datetime, time, timezone

from bson import ObjectId

from Repositories.patient_repository import PatientRepository
from DB.schemas import (
    CreatePatient,
    ReadPatient,
    UpdatePatient,
)
from exceptions.patient import (
    InvalidPatientIdError,
    PatientNotFoundError,
    EmptyPatientUpdateError,
)


class PatientService:

    def __init__(self, repository: PatientRepository):
        self.repository = repository

    @staticmethod
    def _to_read_schema(patient: dict) -> ReadPatient:
        return ReadPatient(
            patient_id=str(patient["_id"]),
            full_name=patient["full_name"],
            date_of_birth=patient["date_of_birth"],
            gender=patient["gender"],
            phone=patient["phone"],
            email=patient.get("email"),
            address=patient.get("address"),
            blood_group=patient.get("blood_group"),
            emergency_contact=patient.get("emergency_contact"),
            created_at=patient["created_at"],
            updated_at=patient["updated_at"],
        )

    async def create_patient(
        self,
        data: CreatePatient,
    ) -> ReadPatient:

        patient_data = data.model_dump()

        patient_data["date_of_birth"] = datetime.combine(
            patient_data["date_of_birth"],
            time.min,
        )

        now = datetime.now(timezone.utc)

        patient_data["created_at"] = now
        patient_data["updated_at"] = now

        patient = await self.repository.create(patient_data)

        return self._to_read_schema(patient)

    async def get_patient_by_id(
        self,
        patient_id: str,
    ) -> ReadPatient:

        try:
            object_id = ObjectId(patient_id)
        except Exception:
            raise InvalidPatientIdError(patient_id)

        patient = await self.repository.get_by_id(object_id)

        if patient is None:
            raise PatientNotFoundError(patient_id)

        return self._to_read_schema(patient)

    async def get_all_patients(
        self,
    ) -> list[ReadPatient]:

        patients = await self.repository.get_all()

        return [self._to_read_schema(patient) for patient in patients]

    async def update_patient(
        self,
        patient_id: str,
        data: UpdatePatient,
    ) -> ReadPatient:

        try:
            object_id = ObjectId(patient_id)
        except Exception:
            raise InvalidPatientIdError(patient_id)

        update_data = data.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )

        if not update_data:
            raise EmptyPatientUpdateError()

        if "date_of_birth" in update_data:
            update_data["date_of_birth"] = datetime.combine(
                update_data["date_of_birth"],
                time.min,
            )

        update_data["updated_at"] = datetime.now(timezone.utc)

        patient = await self.repository.update(
            object_id,
            update_data,
        )

        if patient is None:
            raise PatientNotFoundError(patient_id)

        return self._to_read_schema(patient)

    async def delete_patient(
        self,
        patient_id: str,
    ) -> bool:

        try:
            object_id = ObjectId(patient_id)
        except Exception:
            raise InvalidPatientIdError(patient_id)

        deleted = await self.repository.delete(object_id)

        if not deleted:
            raise PatientNotFoundError(patient_id)

        return True

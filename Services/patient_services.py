from datetime import datetime, time, timezone
import logging
from bson import ObjectId
from bson.errors import InvalidId
from redis.asyncio import Redis

from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

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

    CACHE_TTL = 300  # 5 minutes

    def __init__(
        self,
        repository: PatientRepository,
        redis_client: Redis,
    ):
        self.repository = repository
        self.redis = redis_client

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

    @staticmethod
    def _parse_object_id(patient_id: str) -> ObjectId:
        try:
            return ObjectId(patient_id)
        except (InvalidId, TypeError):
            raise InvalidPatientIdError(patient_id)

    @staticmethod
    def _cache_key(patient_id: ObjectId) -> str:
        return f"patient:{str(patient_id)}"

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

        # No cache invalidation needed: this patient is new.
        return self._to_read_schema(patient)

    async def get_patient_by_id(
        self,
        patient_id: str,
    ) -> ReadPatient:

        object_id = self._parse_object_id(patient_id)
        cache_key = self._cache_key(object_id)

        # Attempt to retrieve the patient from Redis.
        try:
            cached_patient = await self.redis.get(cache_key)

            if cached_patient is not None:
                logger.info("Patient cache hit: %s", patient_id)
                return ReadPatient.model_validate_json(cached_patient)

        except RedisError:
            logger.warning(
                "Redis unavailable; falling back to MongoDB",
                exc_info=True,
            )

        # MongoDB remains the source of truth.
        logger.info("Patient cache miss: %s", patient_id)

        patient = await self.repository.get_by_id(object_id)

        if patient is None:
            raise PatientNotFoundError(patient_id)

        patient_response = self._to_read_schema(patient)

        # Cache the response, but don't fail the request if Redis is down.
        try:
            await self.redis.set(
                cache_key,
                patient_response.model_dump_json(),
                ex=self.CACHE_TTL,
            )
        except RedisError:
            logger.warning(
                "Could not cache patient: %s",
                patient_id,
                exc_info=True,
            )

        return patient_response

    async def get_all_patients(
        self,
    ) -> list[ReadPatient]:

        # List caching is not implemented yet.
        patients = await self.repository.get_all()

        return [self._to_read_schema(patient) for patient in patients]

    async def update_patient(
        self,
        patient_id: str,
        data: UpdatePatient,
    ) -> ReadPatient:

        object_id = self._parse_object_id(patient_id)

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

        # 1. Update MongoDB first.
        patient = await self.repository.update(
            object_id,
            update_data,
        )

        if patient is None:
            raise PatientNotFoundError(patient_id)

        # 2. Invalidate the old cached patient.
        try:
            await self.redis.delete(self._cache_key(object_id))
        except RedisError:
            logger.warning(
                "Could not invalidate patient cache: %s",
                patient_id,
                exc_info=True,
            )

        return self._to_read_schema(patient)

    async def delete_patient(
        self,
        patient_id: str,
    ) -> bool:

        object_id = self._parse_object_id(patient_id)

        # 1. Delete from MongoDB.
        deleted = await self.repository.delete(object_id)

        if not deleted:
            raise PatientNotFoundError(patient_id)

        # 2. Remove any cached copy.
        try:
            await self.redis.delete(self._cache_key(object_id))
        except RedisError:
            logger.warning(
                "Could not invalidate patient cache: %s",
                patient_id,
                exc_info=True,
            )
        return True

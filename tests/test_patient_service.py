import json
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock
from redis.exceptions import ConnectionError as RedisConnectionError

import pytest
from bson import ObjectId

from DB.schemas import CreatePatient, UpdatePatient, Gender
from Services.patient_services import PatientService
from exceptions.patient import (
    EmptyPatientUpdateError,
    InvalidPatientIdError,
    PatientNotFoundError,
)


@pytest.fixture
def repository():
    return AsyncMock()


@pytest.fixture
def redis_client():
    redis = AsyncMock()
    redis.get.return_value = None
    return redis


@pytest.fixture
def service(repository, redis_client):
    return PatientService(
        repository=repository,
        redis_client=redis_client,
    )


@pytest.mark.asyncio
async def test_create_patient(service, repository):
    patient_id = ObjectId()

    created_at = datetime.now(timezone.utc)
    updated_at = created_at

    repository.create.return_value = {
        "_id": patient_id,
        "full_name": "John Doe",
        "date_of_birth": datetime(1995, 5, 20),
        "gender": "male",
        "phone": "9876543210",
        "email": "john@example.com",
        "address": "123 Main Street",
        "blood_group": "O+",
        "emergency_contact": "9876543211",
        "created_at": created_at,
        "updated_at": updated_at,
    }

    data = CreatePatient(
        full_name="John Doe",
        date_of_birth=date(1995, 5, 20),
        gender=Gender.MALE,
        phone="9876543210",
        email="john@example.com",
        address="123 Main Street",
        blood_group="O+",
        emergency_contact="9876543211",
    )

    result = await service.create_patient(data)

    assert result.patient_id == str(patient_id)
    assert result.full_name == "John Doe"
    assert result.date_of_birth == date(1995, 5, 20)
    assert result.gender == "male"
    assert result.phone == "9876543210"
    assert result.email == "john@example.com"
    assert result.address == "123 Main Street"
    assert result.blood_group == "O+"
    assert result.emergency_contact == "9876543211"
    assert result.created_at == created_at
    assert result.updated_at == updated_at

    repository.create.assert_awaited_once()

    created_data = repository.create.call_args.args[0]

    assert created_data["full_name"] == "John Doe"
    assert created_data["date_of_birth"] == datetime(1995, 5, 20)
    assert created_data["gender"] == Gender.MALE
    assert created_data["phone"] == "9876543210"


@pytest.mark.asyncio
async def test_get_patient_by_id(service, repository):
    patient_id = ObjectId()

    created_at = datetime.now(timezone.utc)
    updated_at = created_at

    repository.get_by_id.return_value = {
        "_id": patient_id,
        "full_name": "Jane Doe",
        "date_of_birth": datetime(1998, 8, 15),
        "gender": "female",
        "phone": "9876543210",
        "email": "jane@example.com",
        "address": "456 Park Road",
        "blood_group": "A+",
        "emergency_contact": "9876543211",
        "created_at": created_at,
        "updated_at": updated_at,
    }

    result = await service.get_patient_by_id(str(patient_id))

    assert result.patient_id == str(patient_id)
    assert result.full_name == "Jane Doe"
    assert result.date_of_birth == date(1998, 8, 15)
    assert result.gender == "female"
    assert result.phone == "9876543210"
    assert result.email == "jane@example.com"
    assert result.address == "456 Park Road"
    assert result.blood_group == "A+"
    assert result.emergency_contact == "9876543211"

    repository.get_by_id.assert_awaited_once_with(patient_id)


@pytest.mark.asyncio
async def test_get_patient_by_id_not_found(service, repository):
    patient_id = ObjectId()

    repository.get_by_id.return_value = None

    with pytest.raises(PatientNotFoundError):
        await service.get_patient_by_id(str(patient_id))

    repository.get_by_id.assert_awaited_once_with(patient_id)


@pytest.mark.asyncio
async def test_get_patient_by_id_invalid_id(service, repository):
    with pytest.raises(InvalidPatientIdError):
        await service.get_patient_by_id("not-a-valid-object-id")

    repository.get_by_id.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_all_patients(service, repository):
    patient_id_1 = ObjectId()
    patient_id_2 = ObjectId()

    created_at = datetime.now(timezone.utc)
    updated_at = created_at

    repository.get_all.return_value = [
        {
            "_id": patient_id_1,
            "full_name": "John Doe",
            "date_of_birth": datetime(1995, 5, 20),
            "gender": "male",
            "phone": "9876543210",
            "email": "john@example.com",
            "address": "123 Main Street",
            "blood_group": "O+",
            "emergency_contact": "9876543211",
            "created_at": created_at,
            "updated_at": updated_at,
        },
        {
            "_id": patient_id_2,
            "full_name": "Jane Doe",
            "date_of_birth": datetime(1998, 8, 15),
            "gender": "female",
            "phone": "9876543212",
            "email": "jane@example.com",
            "address": "456 Park Road",
            "blood_group": "A+",
            "emergency_contact": "9876543213",
            "created_at": created_at,
            "updated_at": updated_at,
        },
    ]

    result = await service.get_all_patients()

    assert len(result) == 2

    assert result[0].patient_id == str(patient_id_1)
    assert result[0].full_name == "John Doe"
    assert result[0].date_of_birth == date(1995, 5, 20)

    assert result[1].patient_id == str(patient_id_2)
    assert result[1].full_name == "Jane Doe"
    assert result[1].date_of_birth == date(1998, 8, 15)

    repository.get_all.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_all_patients_returns_empty_list(service, repository):
    repository.get_all.return_value = []

    result = await service.get_all_patients()

    assert result == []

    repository.get_all.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_patient(service, repository, redis_client):
    patient_id = ObjectId()

    created_at = datetime.now(timezone.utc)
    updated_at = datetime.now(timezone.utc)

    repository.update.return_value = {
        "_id": patient_id,
        "full_name": "John Updated",
        "date_of_birth": datetime(1995, 5, 20),
        "gender": "male",
        "phone": "9999999999",
        "email": "john.updated@example.com",
        "address": "Updated Address",
        "blood_group": "O+",
        "emergency_contact": "9999999998",
        "created_at": created_at,
        "updated_at": updated_at,
    }

    data = UpdatePatient(
        full_name="John Updated",
        phone="9999999999",
        email="john.updated@example.com",
    )

    result = await service.update_patient(
        str(patient_id),
        data,
    )

    assert result.patient_id == str(patient_id)
    assert result.full_name == "John Updated"
    assert result.phone == "9999999999"
    assert result.email == "john.updated@example.com"

    repository.update.assert_awaited_once()

    update_args = repository.update.call_args.args

    assert update_args[0] == patient_id
    assert update_args[1]["full_name"] == "John Updated"
    assert update_args[1]["phone"] == "9999999999"
    assert update_args[1]["email"] == "john.updated@example.com"
    assert "updated_at" in update_args[1]
    redis_client.delete.assert_awaited_once_with(f"patient:{patient_id}")


@pytest.mark.asyncio
async def test_update_patient_converts_date_of_birth(
    service,
    repository,
    redis_client,
):
    patient_id = ObjectId()

    created_at = datetime.now(timezone.utc)
    updated_at = datetime.now(timezone.utc)

    repository.update.return_value = {
        "_id": patient_id,
        "full_name": "John Doe",
        "date_of_birth": datetime(2000, 1, 1),
        "gender": "male",
        "phone": "9876543210",
        "email": None,
        "address": None,
        "blood_group": None,
        "emergency_contact": None,
        "created_at": created_at,
        "updated_at": updated_at,
    }

    data = UpdatePatient(
        date_of_birth=date(2000, 1, 1),
    )

    result = await service.update_patient(
        str(patient_id),
        data,
    )

    assert result.date_of_birth == date(2000, 1, 1)

    update_data = repository.update.call_args.args[1]

    assert update_data["date_of_birth"] == datetime(2000, 1, 1)
    assert "updated_at" in update_data
    redis_client.delete.assert_awaited_once_with(f"patient:{patient_id}")


@pytest.mark.asyncio
async def test_update_patient_with_no_data(service):
    patient_id = ObjectId()

    data = UpdatePatient()

    with pytest.raises(EmptyPatientUpdateError):
        await service.update_patient(
            str(patient_id),
            data,
        )


@pytest.mark.asyncio
async def test_update_patient_invalid_id(service, repository):
    data = UpdatePatient(
        full_name="Updated Name",
    )

    with pytest.raises(InvalidPatientIdError):
        await service.update_patient(
            "not-a-valid-object-id",
            data,
        )

    repository.update.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_patient_not_found(service, repository):
    patient_id = ObjectId()

    repository.update.return_value = None

    data = UpdatePatient(
        full_name="Updated Name",
    )

    with pytest.raises(PatientNotFoundError):
        await service.update_patient(
            str(patient_id),
            data,
        )

    repository.update.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_patient(service, repository, redis_client):
    patient_id = ObjectId()

    repository.delete.return_value = True

    result = await service.delete_patient(str(patient_id))

    assert result is True

    repository.delete.assert_awaited_once_with(patient_id)
    redis_client.delete.assert_awaited_once_with(f"patient:{patient_id}")


@pytest.mark.asyncio
async def test_delete_patient_invalid_id(service, repository):
    with pytest.raises(InvalidPatientIdError):
        await service.delete_patient("not-a-valid-object-id")

    repository.delete.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_patient_not_found(service, repository):
    patient_id = ObjectId()

    repository.delete.return_value = False

    with pytest.raises(PatientNotFoundError):
        await service.delete_patient(str(patient_id))

    repository.delete.assert_awaited_once_with(patient_id)


@pytest.mark.asyncio
async def test_get_patient_cache_hit(
    service,
    repository,
    redis_client,
):
    patient_id = ObjectId()
    now = datetime.now(timezone.utc)

    cached_patient = {
        "patient_id": str(patient_id),
        "full_name": "Jane Doe",
        "date_of_birth": "1998-08-15",
        "gender": "female",
        "phone": "9876543210",
        "email": "jane@example.com",
        "address": None,
        "blood_group": None,
        "emergency_contact": None,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }

    redis_client.get.return_value = json.dumps(cached_patient)

    result = await service.get_patient_by_id(str(patient_id))

    assert result.full_name == "Jane Doe"
    redis_client.get.assert_awaited_once_with(f"patient:{patient_id}")

    # Redis served the response, so MongoDB was not queried.
    repository.get_by_id.assert_not_awaited()
    redis_client.set.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_patient_cache_miss(
    service,
    repository,
    redis_client,
):
    patient_id = ObjectId()
    now = datetime.now(timezone.utc)

    redis_client.get.return_value = None

    repository.get_by_id.return_value = {
        "_id": patient_id,
        "full_name": "Jane Doe",
        "date_of_birth": datetime(1998, 8, 15),
        "gender": "female",
        "phone": "9876543210",
        "email": None,
        "address": None,
        "blood_group": None,
        "emergency_contact": None,
        "created_at": now,
        "updated_at": now,
    }

    result = await service.get_patient_by_id(str(patient_id))

    assert result.full_name == "Jane Doe"

    repository.get_by_id.assert_awaited_once_with(patient_id)

    redis_client.set.assert_awaited_once()
    assert redis_client.set.await_args.args[0] == (f"patient:{patient_id}")
    assert redis_client.set.await_args.kwargs["ex"] == 300


@pytest.mark.asyncio
async def test_get_patient_redis_unavailable(
    service,
    repository,
    redis_client,
):
    patient_id = ObjectId()
    now = datetime.now(timezone.utc)

    redis_client.get.side_effect = RedisConnectionError("Redis unavailable")

    repository.get_by_id.return_value = {
        "_id": patient_id,
        "full_name": "Jane Doe",
        "date_of_birth": datetime(1998, 8, 15),
        "gender": "female",
        "phone": "9876543210",
        "email": None,
        "address": None,
        "blood_group": None,
        "emergency_contact": None,
        "created_at": now,
        "updated_at": now,
    }

    result = await service.get_patient_by_id(str(patient_id))

    assert result.full_name == "Jane Doe"
    repository.get_by_id.assert_awaited_once_with(patient_id)


@pytest.mark.asyncio
async def test_delete_patient_invalidates_cache(
    service,
    repository,
    redis_client,
):
    patient_id = ObjectId()
    repository.delete.return_value = True

    result = await service.delete_patient(str(patient_id))

    assert result is True
    repository.delete.assert_awaited_once_with(patient_id)
    redis_client.delete.assert_awaited_once_with(f"patient:{patient_id}")


@pytest.mark.asyncio
async def test_delete_patient_when_redis_unavailable(
    service,
    repository,
    redis_client,
):
    patient_id = ObjectId()
    repository.delete.return_value = True

    redis_client.delete.side_effect = RedisConnectionError("Redis unavailable")

    result = await service.delete_patient(str(patient_id))

    assert result is True
    repository.delete.assert_awaited_once_with(patient_id)
    redis_client.delete.assert_awaited_once_with(f"patient:{patient_id}")


@pytest.mark.asyncio
async def test_get_patient_when_cache_write_fails(
    service,
    repository,
    redis_client,
):
    patient_id = ObjectId()
    now = datetime.now(timezone.utc)
    repository.get_by_id.return_value = {
        "_id": patient_id,
        "full_name": "Jane Doe",
        "date_of_birth": datetime(1998, 8, 15),
        "gender": "female",
        "phone": "9876543210",
        "created_at": now,
        "updated_at": now,
    }
    redis_client.set.side_effect = RedisConnectionError("Redis unavailable")

    result = await service.get_patient_by_id(str(patient_id))

    assert result.full_name == "Jane Doe"
    repository.get_by_id.assert_awaited_once_with(patient_id)
    redis_client.set.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_patient_when_redis_unavailable(
    service,
    repository,
    redis_client,
):
    patient_id = ObjectId()
    now = datetime.now(timezone.utc)
    repository.update.return_value = {
        "_id": patient_id,
        "full_name": "Updated Name",
        "date_of_birth": datetime(1998, 8, 15),
        "gender": "female",
        "phone": "9876543210",
        "created_at": now,
        "updated_at": now,
    }
    redis_client.delete.side_effect = RedisConnectionError("Redis unavailable")

    result = await service.update_patient(
        str(patient_id), UpdatePatient(full_name="Updated Name")
    )

    assert result.full_name == "Updated Name"
    repository.update.assert_awaited_once()
    redis_client.delete.assert_awaited_once_with(f"patient:{patient_id}")


@pytest.mark.asyncio
async def test_patient_not_found_does_not_cache(
    service,
    repository,
    redis_client,
):
    patient_id = ObjectId()
    repository.get_by_id.return_value = None

    with pytest.raises(PatientNotFoundError):
        await service.get_patient_by_id(str(patient_id))

    redis_client.set.assert_not_awaited()

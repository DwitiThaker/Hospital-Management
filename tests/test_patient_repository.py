from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from bson import ObjectId

from Repositories.patient_repository import PatientRepository


@pytest.fixture
def collection():
    collection = MagicMock()

    collection.insert_one = AsyncMock()
    collection.find_one = AsyncMock()
    collection.find = MagicMock()
    collection.update_one = AsyncMock()
    collection.delete_one = AsyncMock()

    return collection


@pytest.fixture
def repository(collection):
    return PatientRepository(collection)


@pytest.fixture
def patient_id():
    return ObjectId()


@pytest.fixture
def patient_document(patient_id):
    now = datetime.now(timezone.utc)

    return {
        "_id": patient_id,
        "full_name": "John Doe",
        "date_of_birth": datetime(1995, 5, 20),
        "gender": "male",
        "phone": "9876543210",
        "email": "john@example.com",
        "address": "123 Main Street",
        "blood_group": "O+",
        "emergency_contact": "9876543211",
        "created_at": now,
        "updated_at": now,
    }


@pytest.mark.asyncio
async def test_create_patient(
    repository,
    collection,
    patient_document,
):
    patient_data = {
        "full_name": "John Doe",
        "date_of_birth": datetime(1995, 5, 20),
        "gender": "male",
        "phone": "9876543210",
        "email": "john@example.com",
        "address": "123 Main Street",
        "blood_group": "O+",
        "emergency_contact": "9876543211",
        "created_at": patient_document["created_at"],
        "updated_at": patient_document["updated_at"],
    }

    insert_result = MagicMock()
    insert_result.inserted_id = patient_document["_id"]

    collection.insert_one.return_value = insert_result
    collection.find_one.return_value = patient_document

    result = await repository.create(patient_data)

    collection.insert_one.assert_awaited_once_with(patient_data)

    collection.find_one.assert_awaited_once_with({"_id": patient_document["_id"]})

    assert result == patient_document


@pytest.mark.asyncio
async def test_create_patient_raises_when_document_cannot_be_retrieved(
    repository,
    collection,
    patient_id,
):
    patient_data = {
        "full_name": "John Doe",
        "date_of_birth": datetime(1995, 5, 20),
        "gender": "male",
        "phone": "9876543210",
        "email": None,
        "address": None,
        "blood_group": None,
        "emergency_contact": "9876543211",
    }

    insert_result = MagicMock()
    insert_result.inserted_id = patient_id

    collection.insert_one.return_value = insert_result
    collection.find_one.return_value = None

    with pytest.raises(
        RuntimeError,
        match="could not be retrieved",
    ):
        await repository.create(patient_data)


@pytest.mark.asyncio
async def test_get_patient_by_id(
    repository,
    collection,
    patient_id,
    patient_document,
):
    collection.find_one.return_value = patient_document

    result = await repository.get_by_id(patient_id)

    collection.find_one.assert_awaited_once_with({"_id": patient_id})

    assert result == patient_document


@pytest.mark.asyncio
async def test_get_patient_by_id_returns_none(
    repository,
    collection,
    patient_id,
):
    collection.find_one.return_value = None

    result = await repository.get_by_id(patient_id)

    collection.find_one.assert_awaited_once_with({"_id": patient_id})

    assert result is None


@pytest.mark.asyncio
async def test_get_all_patients(
    repository,
    collection,
    patient_document,
):
    cursor = MagicMock()

    cursor.to_list = AsyncMock(return_value=[patient_document])

    collection.find.return_value = cursor

    result = await repository.get_all()

    collection.find.assert_called_once_with()

    cursor.to_list.assert_awaited_once()

    assert result == [patient_document]


@pytest.mark.asyncio
async def test_get_all_patients_returns_empty_list(
    repository,
    collection,
):
    cursor = MagicMock()

    cursor.to_list = AsyncMock(return_value=[])

    collection.find.return_value = cursor

    result = await repository.get_all()

    collection.find.assert_called_once_with()

    cursor.to_list.assert_awaited_once()

    assert result == []


@pytest.mark.asyncio
async def test_update_patient(
    repository,
    collection,
    patient_id,
    patient_document,
):
    update_data = {
        "full_name": "John Updated",
        "phone": "9999999999",
    }

    update_result = MagicMock()
    update_result.matched_count = 1

    collection.update_one.return_value = update_result
    collection.find_one.return_value = patient_document

    result = await repository.update(
        patient_id,
        update_data,
    )

    collection.update_one.assert_awaited_once_with(
        {"_id": patient_id},
        {"$set": update_data},
    )

    collection.find_one.assert_awaited_once_with({"_id": patient_id})

    assert result == patient_document


@pytest.mark.asyncio
async def test_update_patient_returns_none_when_not_found(
    repository,
    collection,
    patient_id,
):
    update_data = {
        "full_name": "John Updated",
    }

    update_result = MagicMock()
    update_result.matched_count = 0

    collection.update_one.return_value = update_result

    result = await repository.update(
        patient_id,
        update_data,
    )

    collection.find_one.assert_not_awaited()

    assert result is None


@pytest.mark.asyncio
async def test_delete_patient(
    repository,
    collection,
    patient_id,
):
    delete_result = MagicMock()
    delete_result.deleted_count = 1

    collection.delete_one.return_value = delete_result

    result = await repository.delete(patient_id)

    collection.delete_one.assert_awaited_once_with({"_id": patient_id})

    assert result is True


@pytest.mark.asyncio
async def test_delete_patient_returns_false_when_not_found(
    repository,
    collection,
    patient_id,
):
    delete_result = MagicMock()
    delete_result.deleted_count = 0

    collection.delete_one.return_value = delete_result

    result = await repository.delete(patient_id)

    collection.delete_one.assert_awaited_once_with({"_id": patient_id})

    assert result is False

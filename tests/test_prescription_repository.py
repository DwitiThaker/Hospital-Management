from unittest.mock import AsyncMock, MagicMock

import pytest
from bson import ObjectId

from Repositories.prescription_repository import PrescriptionRepository


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
    return PrescriptionRepository(collection)


@pytest.fixture
def prescription_id():
    return ObjectId()


@pytest.fixture
def prescription_document(prescription_id):
    medicine_id = ObjectId()
    doctor_id = ObjectId()

    return {
        "_id": prescription_id,
        "doctor_id": doctor_id,
        "patient_id": "patient-123",
        "patient_name": "John Doe",
        "description": "Take medicine after meals",
        "duration_days": 7,
        "medicines": [
            {
                "medicine_id": medicine_id,
                "quantity": 2,
            }
        ],
    }


@pytest.mark.asyncio
async def test_create_prescription(
    repository,
    collection,
    prescription_document,
):
    prescription_data = {
        "doctor_id": prescription_document["doctor_id"],
        "patient_id": prescription_document["patient_id"],
        "patient_name": prescription_document["patient_name"],
        "description": prescription_document["description"],
        "duration_days": prescription_document["duration_days"],
        "medicines": prescription_document["medicines"],
    }

    insert_result = MagicMock()
    insert_result.inserted_id = prescription_document["_id"]

    collection.insert_one.return_value = insert_result
    collection.find_one.return_value = prescription_document

    result = await repository.create(prescription_data)

    collection.insert_one.assert_awaited_once_with(
        prescription_data
    )

    collection.find_one.assert_awaited_once_with(
        {"_id": prescription_document["_id"]}
    )

    assert result == prescription_document


@pytest.mark.asyncio
async def test_create_prescription_raises_when_document_cannot_be_retrieved(
    repository,
    collection,
    prescription_id,
):
    prescription_data = {
        "patient_id": "patient-123",
        "patient_name": "John Doe",
        "description": "Take medicine after meals",
        "duration_days": 7,
        "medicines": [],
    }

    insert_result = MagicMock()
    insert_result.inserted_id = prescription_id

    collection.insert_one.return_value = insert_result
    collection.find_one.return_value = None

    with pytest.raises(RuntimeError, match="could not be retrieved"):
        await repository.create(prescription_data)


@pytest.mark.asyncio
async def test_get_prescription_by_id(
    repository,
    collection,
    prescription_id,
    prescription_document,
):
    collection.find_one.return_value = prescription_document

    result = await repository.get_by_id(prescription_id)

    collection.find_one.assert_awaited_once_with(
        {"_id": prescription_id}
    )

    assert result == prescription_document


@pytest.mark.asyncio
async def test_get_prescription_by_id_returns_none(
    repository,
    collection,
    prescription_id,
):
    collection.find_one.return_value = None

    result = await repository.get_by_id(prescription_id)

    assert result is None


@pytest.mark.asyncio
async def test_get_all_prescriptions(
    repository,
    collection,
    prescription_document,
):
    cursor = MagicMock()
    cursor.to_list = AsyncMock(return_value=[prescription_document])

    collection.find.return_value = cursor

    result = await repository.get_all()

    collection.find.assert_called_once_with()
    cursor.to_list.assert_awaited_once()

    assert result == [prescription_document]


@pytest.mark.asyncio
async def test_get_all_prescriptions_returns_empty_list(
    repository,
    collection,
):
    cursor = MagicMock()
    cursor.to_list = AsyncMock(return_value=[])

    collection.find.return_value = cursor

    result = await repository.get_all()

    assert result == []


@pytest.mark.asyncio
async def test_update_prescription(
    repository,
    collection,
    prescription_id,
    prescription_document,
):
    update_data = {
        "description": "Take medicine before meals",
    }

    update_result = MagicMock()
    update_result.matched_count = 1

    collection.update_one.return_value = update_result
    collection.find_one.return_value = prescription_document

    result = await repository.update(
        prescription_id,
        update_data,
    )

    collection.update_one.assert_awaited_once_with(
        {"_id": prescription_id},
        {"$set": update_data},
    )

    collection.find_one.assert_awaited_once_with(
        {"_id": prescription_id}
    )

    assert result == prescription_document


@pytest.mark.asyncio
async def test_update_prescription_returns_none_when_not_found(
    repository,
    collection,
    prescription_id,
):
    update_data = {
        "description": "Updated description",
    }

    update_result = MagicMock()
    update_result.matched_count = 0

    collection.update_one.return_value = update_result

    result = await repository.update(
        prescription_id,
        update_data,
    )

    collection.find_one.assert_not_awaited()

    assert result is None


@pytest.mark.asyncio
async def test_delete_prescription(
    repository,
    collection,
    prescription_id,
):
    delete_result = MagicMock()
    delete_result.deleted_count = 1

    collection.delete_one.return_value = delete_result

    result = await repository.delete(prescription_id)

    collection.delete_one.assert_awaited_once_with(
        {"_id": prescription_id}
    )

    assert result is True


@pytest.mark.asyncio
async def test_delete_prescription_returns_false_when_not_found(
    repository,
    collection,
    prescription_id,
):
    delete_result = MagicMock()
    delete_result.deleted_count = 0

    collection.delete_one.return_value = delete_result

    result = await repository.delete(prescription_id)

    assert result is False

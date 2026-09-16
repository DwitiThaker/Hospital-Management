from unittest.mock import AsyncMock, MagicMock

import pytest
from bson import ObjectId

from Repositories.medicine_repository import MedicineRepository


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
    return MedicineRepository(collection)


@pytest.fixture
def medicine_id():
    return ObjectId()


@pytest.fixture
def medicine_document(medicine_id):
    return {
        "_id": medicine_id,
        "name": "Paracetamol",
        "quantity": 100,
        "price": 25,
        "expiry": "2027-12-31",
    }


@pytest.mark.asyncio
async def test_create_medicine(repository, collection, medicine_document):
    medicine_data = {
        "name": "Paracetamol",
        "quantity": 100,
        "price": 25,
    }

    insert_result = MagicMock()
    insert_result.inserted_id = medicine_document["_id"]

    collection.insert_one.return_value = insert_result
    collection.find_one.return_value = medicine_document

    result = await repository.create(medicine_data)

    collection.insert_one.assert_awaited_once_with(medicine_data)
    collection.find_one.assert_awaited_once_with(
        {"_id": medicine_document["_id"]}
    )

    assert result == medicine_document


@pytest.mark.asyncio
async def test_create_medicine_raises_when_document_cannot_be_retrieved(
    repository,
    collection,
    medicine_id,
):
    medicine_data = {
        "name": "Paracetamol",
        "quantity": 100,
        "price": 25,
    }

    insert_result = MagicMock()
    insert_result.inserted_id = medicine_id

    collection.insert_one.return_value = insert_result
    collection.find_one.return_value = None

    with pytest.raises(RuntimeError, match="could not be retrieved"):
        await repository.create(medicine_data)


@pytest.mark.asyncio
async def test_get_medicine_by_id(
    repository,
    collection,
    medicine_id,
    medicine_document,
):
    collection.find_one.return_value = medicine_document

    result = await repository.get_by_id(medicine_id)

    collection.find_one.assert_awaited_once_with(
        {"_id": medicine_id}
    )

    assert result == medicine_document


@pytest.mark.asyncio
async def test_get_medicine_by_id_returns_none(
    repository,
    collection,
    medicine_id,
):
    collection.find_one.return_value = None

    result = await repository.get_by_id(medicine_id)

    assert result is None


@pytest.mark.asyncio
async def test_get_all_medicines(
    repository,
    collection,
    medicine_document,
):
    cursor = MagicMock()
    cursor.to_list = AsyncMock(return_value=[medicine_document])

    collection.find.return_value = cursor

    result = await repository.get_all()

    collection.find.assert_called_once_with()
    cursor.to_list.assert_awaited_once()

    assert result == [medicine_document]


@pytest.mark.asyncio
async def test_get_all_medicines_returns_empty_list(
    repository,
    collection,
):
    cursor = MagicMock()
    cursor.to_list = AsyncMock(return_value=[])

    collection.find.return_value = cursor

    result = await repository.get_all()

    assert result == []


@pytest.mark.asyncio
async def test_update_medicine(
    repository,
    collection,
    medicine_id,
    medicine_document,
):
    update_data = {
        "quantity": 150,
    }

    update_result = MagicMock()
    update_result.matched_count = 1

    collection.update_one.return_value = update_result
    collection.find_one.return_value = medicine_document

    result = await repository.update(
        medicine_id,
        update_data,
    )

    collection.update_one.assert_awaited_once_with(
        {"_id": medicine_id},
        {"$set": update_data},
    )

    collection.find_one.assert_awaited_once_with(
        {"_id": medicine_id}
    )

    assert result == medicine_document


@pytest.mark.asyncio
async def test_update_medicine_returns_none_when_not_found(
    repository,
    collection,
    medicine_id,
):
    update_data = {
        "quantity": 150,
    }

    update_result = MagicMock()
    update_result.matched_count = 0

    collection.update_one.return_value = update_result

    result = await repository.update(
        medicine_id,
        update_data,
    )

    collection.find_one.assert_not_awaited()

    assert result is None


@pytest.mark.asyncio
async def test_delete_medicine(
    repository,
    collection,
    medicine_id,
):
    delete_result = MagicMock()
    delete_result.deleted_count = 1

    collection.delete_one.return_value = delete_result

    result = await repository.delete(medicine_id)

    collection.delete_one.assert_awaited_once_with(
        {"_id": medicine_id}
    )

    assert result is True


@pytest.mark.asyncio
async def test_delete_medicine_returns_false_when_not_found(
    repository,
    collection,
    medicine_id,
):
    delete_result = MagicMock()
    delete_result.deleted_count = 0

    collection.delete_one.return_value = delete_result

    result = await repository.delete(medicine_id)

    assert result is False

from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest
from bson import ObjectId

from DB.schemas import CreateMedicine, UpdateMedicine
from Services.medicine_services import MedicineService
from exceptions.medicine import (
    EmptyMedicineUpdateError,
    InvalidMedicineIdError,
    MedicineNotFoundError,
)


@pytest.fixture
def repository():
    return AsyncMock()


@pytest.fixture
def service(repository):
    return MedicineService(repository)


@pytest.mark.asyncio
async def test_create_medicine(service, repository):
    medicine_id = ObjectId()

    repository.create.return_value = {
        "_id": medicine_id,
        "name": "Paracetamol",
        "quantity": 100,
        "price": Decimal("25.50"),
        "expiry": date(2027, 12, 31),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    data = CreateMedicine(
        name="Paracetamol",
        quantity=100,
        price=Decimal("25.50"),
        expiry=date(2027, 12, 31),
    )

    result = await service.create_medicine(data)

    assert result.id == str(medicine_id)
    assert result.name == "Paracetamol"
    assert result.quantity == 100
    assert result.price == Decimal("25.50")

    repository.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_medicine(service, repository):
    medicine_id = ObjectId()

    repository.get_by_id.return_value = {
        "_id": medicine_id,
        "name": "Ibuprofen",
        "quantity": 50,
        "price": Decimal("40.00"),
        "expiry": date(2027, 6, 30),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    result = await service.get_medicine(str(medicine_id))

    assert result.id == str(medicine_id)
    assert result.name == "Ibuprofen"
    assert result.quantity == 50

    repository.get_by_id.assert_awaited_once_with(medicine_id)


@pytest.mark.asyncio
async def test_get_medicine_not_found(service, repository):
    medicine_id = ObjectId()

    repository.get_by_id.return_value = None

    with pytest.raises(MedicineNotFoundError):
        await service.get_medicine(str(medicine_id))


@pytest.mark.asyncio
async def test_get_medicine_invalid_id(service):
    with pytest.raises(InvalidMedicineIdError):
        await service.get_medicine("not-a-valid-object-id")

@pytest.mark.asyncio
async def test_update_medicine(service, repository):
    medicine_id = ObjectId()

    repository.update.return_value = {
        "_id": medicine_id,
        "name": "Paracetamol",
        "quantity": 100,
        "price": Decimal("30.00"),
        "expiry": date(2028, 1, 1),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    data = UpdateMedicine(
        price=Decimal("30.00")
    )

    result = await service.update_medicine(
        str(medicine_id),
        data,
    )

    assert result.price == Decimal("30.00")

    repository.update.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_medicine_with_no_data(service):
    medicine_id = ObjectId()

    data = UpdateMedicine()

    with pytest.raises(EmptyMedicineUpdateError):
        await service.update_medicine(
            str(medicine_id),
            data,
        )


@pytest.mark.asyncio
async def test_delete_medicine(service, repository):
    medicine_id = ObjectId()

    repository.delete.return_value = True

    result = await service.delete_medicine(
        str(medicine_id)
    )

    assert result is None

    repository.delete.assert_awaited_once_with(medicine_id)


@pytest.mark.asyncio
async def test_list_medicines(service, repository):
    medicine_id = ObjectId()

    repository.get_all.return_value = [
        {
            "_id": medicine_id,
            "name": "Paracetamol",
            "quantity": 100,
            "price": Decimal("25.50"),
            "expiry": date(2027, 12, 31),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    ]

    result = await service.list_medicines()

    assert len(result) == 1
    assert result[0].id == str(medicine_id)
    assert result[0].name == "Paracetamol"

    repository.get_all.assert_awaited_once()
from datetime import datetime, timezone

import pytest
from bson import ObjectId
from unittest.mock import AsyncMock

from DB.schemas import (
    CreatePrescription,
    UpdatePrescription,
)
from Services.prescription_services import PrescriptionService
from exceptions.prescription import (
    EmptyPrescriptionUpdateError,
    InvalidPrescriptionIdError,
    PrescriptionNotFoundError,
)


@pytest.fixture
def repository():
    return AsyncMock()


@pytest.fixture
def service(repository):
    return PrescriptionService(repository)


@pytest.fixture
def prescription_document():
    prescription_id = ObjectId()
    medicine_id = ObjectId()
    now = datetime.now(timezone.utc)

    return {
        "_id": prescription_id,
        "patient_id": "1",
        "doctor_id": ObjectId(),
        "patient_name": "Dwiti",
        "description": "Cold medicine test",
        "medicines": [
            {
                "medicine_id": medicine_id,
                "quantity": 1,
            }
        ],
        "duration_days": 7,
        "issued_at": now,
        "created_at": now,
        "updated_at": now,
    }


@pytest.mark.asyncio
async def test_create_prescription(
    service,
    repository,
    prescription_document,
):
    repository.create.return_value = prescription_document

    data = CreatePrescription(
        patient_id="1",
        patient_name="Dwiti",
        description="Cold medicine test",
        duration_days=7,
        medicines=[
            {
                "medicine_id": str(
                    prescription_document["medicines"][0]["medicine_id"]
                ),
                "quantity": 1,
            }
        ],
        issued_at=datetime.now(timezone.utc),
    )

    result = await service.create_prescription(
        data,
        doctor_id=str(prescription_document["doctor_id"]),
    )

    assert result.prescription_id == str(prescription_document["_id"])
    assert result.patient_name == "Dwiti"
    assert result.duration_days == 7

    repository.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_prescription(
    service,
    repository,
    prescription_document,
):
    prescription_id = prescription_document["_id"]
    repository.get_by_id.return_value = prescription_document

    result = await service.get_prescription(str(prescription_id))

    assert result.prescription_id == str(prescription_id)
    assert result.patient_name == "Dwiti"

    repository.get_by_id.assert_awaited_once_with(prescription_id)


@pytest.mark.asyncio
async def test_get_prescription_not_found(
    service,
    repository,
):
    prescription_id = ObjectId()
    repository.get_by_id.return_value = None

    with pytest.raises(PrescriptionNotFoundError):
        await service.get_prescription(str(prescription_id))


@pytest.mark.asyncio
async def test_get_prescription_invalid_id(service):
    with pytest.raises(InvalidPrescriptionIdError):
        await service.get_prescription("not-a-valid-object-id")


@pytest.mark.asyncio
async def test_list_prescriptions(
    service,
    repository,
    prescription_document,
):
    repository.get_all.return_value = [prescription_document]

    result = await service.list_prescriptions()

    assert len(result) == 1
    assert result[0].prescription_id == str(prescription_document["_id"])

    repository.get_all.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_prescription(
    service,
    repository,
    prescription_document,
):
    prescription_id = prescription_document["_id"]

    updated_document = {
        **prescription_document,
        "duration_days": 14,
    }

    repository.update.return_value = updated_document

    data = UpdatePrescription(duration_days=14)

    result = await service.update_prescription(
        str(prescription_id),
        data,
    )

    assert result.duration_days == 14

    repository.update.assert_awaited_once()

    update_data = repository.update.await_args.args[1]

    assert update_data["duration_days"] == 14
    assert "updated_at" in update_data


@pytest.mark.asyncio
async def test_update_prescription_empty_data(service):
    prescription_id = ObjectId()

    data = UpdatePrescription()

    with pytest.raises(EmptyPrescriptionUpdateError):
        await service.update_prescription(
            str(prescription_id),
            data,
        )


@pytest.mark.asyncio
async def test_update_prescription_not_found(
    service,
    repository,
):
    prescription_id = ObjectId()
    repository.update.return_value = None

    data = UpdatePrescription(duration_days=14)

    with pytest.raises(PrescriptionNotFoundError):
        await service.update_prescription(
            str(prescription_id),
            data,
        )


@pytest.mark.asyncio
async def test_update_prescription_invalid_id(service):
    data = UpdatePrescription(duration_days=14)

    with pytest.raises(InvalidPrescriptionIdError):
        await service.update_prescription(
            "not-a-valid-object-id",
            data,
        )


@pytest.mark.asyncio
async def test_delete_prescription(
    service,
    repository,
):
    prescription_id = ObjectId()
    repository.delete.return_value = True

    result = await service.delete_prescription(str(prescription_id))

    assert result is None

    repository.delete.assert_awaited_once_with(prescription_id)


@pytest.mark.asyncio
async def test_delete_prescription_not_found(
    service,
    repository,
):
    prescription_id = ObjectId()
    repository.delete.return_value = False

    with pytest.raises(PrescriptionNotFoundError):
        await service.delete_prescription(str(prescription_id))


@pytest.mark.asyncio
async def test_delete_prescription_invalid_id(service):
    with pytest.raises(InvalidPrescriptionIdError):
        await service.delete_prescription("not-a-valid-object-id")

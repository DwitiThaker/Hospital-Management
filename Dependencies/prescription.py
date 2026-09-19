from DB.mongodb import prescription_collection
from Repositories.prescription_repository import PrescriptionRepository
from Services.prescription_services import PrescriptionService


def get_prescription_service() -> PrescriptionService:
    repository = PrescriptionRepository(prescription_collection)
    return PrescriptionService(repository)

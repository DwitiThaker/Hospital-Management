from MongoDB.mongodb import medicine_collection
from Repositories.medicine_repository import MedicineRepository
from Services.medicine_services import MedicineService


def get_medicine_service() -> MedicineService:
    repository = MedicineRepository(medicine_collection)

    return MedicineService(repository)

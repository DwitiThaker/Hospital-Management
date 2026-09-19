from DB.mongodb import patient_collection
from Repositories.patient_repository import PatientRepository
from Services.patient_services import PatientService

def get_patient_service() -> PatientService:
    repository = PatientRepository(patient_collection)
    return PatientService(repository)

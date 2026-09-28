class PatientNotFoundError(Exception):
    def __init__(self, patient_id: str):
        self.patient_id = patient_id
        super().__init__(f"Patient '{patient_id}' not found")


class InvalidPatientIdError(Exception):
    def __init__(self, patient_id: str):
        self.patient_id = patient_id
        super().__init__(f"Invalid patient ID: '{patient_id}'")


class EmptyPatientUpdateError(Exception):
    def __init__(self):
        super().__init__("No data provided for update")

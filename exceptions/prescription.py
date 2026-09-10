class PrescriptionNotFoundError(Exception):
    def __init__(self, prescription_id: str):
        self.prescription_id = prescription_id
        super().__init__(f"Prescription '{prescription_id}' not found")


class InvalidPrescriptionIdError(Exception):
    def __init__(self, prescription_id: str):
        self.prescription_id = prescription_id
        super().__init__(f"Invalid prescription ID: '{prescription_id}'")


class EmptyPrescriptionUpdateError(Exception):
    def __init__(self):
        super().__init__("No data provided for update")

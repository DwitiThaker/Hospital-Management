class MedicineNotFoundError(Exception):
    def __init__(self, medicine_id: str):
        self.medicine_id = medicine_id
        super().__init__(f"Medicine '{medicine_id}' not found")


class InvalidMedicineIdError(Exception):
    def __init__(self, medicine_id: str):
        self.medicine_id = medicine_id
        super().__init__(f"Invalid medicine ID: '{medicine_id}'")


class EmptyMedicineUpdateError(Exception):
    def __init__(self):
        super().__init__("No data provided for update")

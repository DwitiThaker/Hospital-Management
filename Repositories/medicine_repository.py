from typing import Optional

from bson import ObjectId
from pymongo.collection import Collection


class  MedicineRepository:

    def __init__(self, collection: Collection):
        self.collection = collection

        
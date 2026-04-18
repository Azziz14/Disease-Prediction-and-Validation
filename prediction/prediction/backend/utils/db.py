from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure
import logging

logger = logging.getLogger(__name__)

class MongoDBClient:
    _instance = None

    def __new__(cls, uri="mongodb://localhost:27017/", db_name="healthcare_ai"):
        if cls._instance is None:
            cls._instance = super(MongoDBClient, cls).__new__(cls)
            try:
                cls._instance.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
                cls._instance.client.admin.command('ping')
                cls._instance.db = cls._instance.client[db_name]
                cls._instance._initialize_collections()
                logger.info(f"Connected to MongoDB: {uri} / Database: {db_name}")
            except ConnectionFailure as e:
                logger.error(f"Failed to connect to MongoDB at {uri}: {e}")
                cls._instance.client = None
                cls._instance.db = None
        return cls._instance

    def _initialize_collections(self):
        """Create collections and enforce necessary indexes."""
        if self.db is None:
            return

        # Users collection
        if 'users' not in self.db.list_collection_names():
            self.db.create_collection('users')
        self.db.users.create_index([("email", ASCENDING)], unique=True)
        self.db.users.create_index([("role", ASCENDING)])

        # Patients collection
        if 'patients' not in self.db.list_collection_names():
            self.db.create_collection('patients')
        self.db.patients.create_index([("user_id", ASCENDING)], unique=True)

        # Doctors collection
        if 'doctors' not in self.db.list_collection_names():
            self.db.create_collection('doctors')
        self.db.doctors.create_index([("user_id", ASCENDING)], unique=True)

        # Medical Records (History)
        if 'medical_records' not in self.db.list_collection_names():
            self.db.create_collection('medical_records')
        self.db.medical_records.create_index([("patient_id", ASCENDING)])
        self.db.medical_records.create_index([("date", DESCENDING)])
        # Text index for Semantic/Keyword search fallbacks
        self.db.medical_records.create_index([("description", "text"), ("diagnosis", "text")])

        # Prescriptions
        if 'prescriptions' not in self.db.list_collection_names():
            self.db.create_collection('prescriptions')
        self.db.prescriptions.create_index([("patient_id", ASCENDING)])
        self.db.prescriptions.create_index([("date_uploaded", DESCENDING)])

        # Predictions Logging
        if 'predictions' not in self.db.list_collection_names():
            self.db.create_collection('predictions')
        self.db.predictions.create_index([("patient_id", ASCENDING)])
        self.db.predictions.create_index([("timestamp", DESCENDING)])

# Global singleton
db_client = MongoDBClient()

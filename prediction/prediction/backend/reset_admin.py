from utils.db import db_client
from utils.auth_store import ensure_default_admin
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def reset():
    admin_email = "admin@123"
    
    if db_client.db is not None:
        logger.info(f"Connected to MongoDB. Searching for {admin_email}...")
        result = db_client.db.users.delete_many({"email": admin_email})
        logger.info(f"Deleted {result.deleted_count} existing admin record(s).")
    else:
        logger.info("MongoDB client not available. Skipping DB reset.")

    logger.info("Invoking fresh admin creation...")
    ensure_default_admin()
    logger.info("Admin recovery complete.")

if __name__ == "__main__":
    reset()

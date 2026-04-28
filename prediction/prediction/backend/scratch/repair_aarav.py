from utils.db import db_client

target_id = 'pat_a388885b'
patient_name = 'Aarav Gupta'

print(f"Healing records for {patient_name} -> {target_id}")

# 1. Update medical_records
res1 = db_client.db.medical_records.update_many(
    {'patient_name': patient_name},
    {'$set': {'patient_id': target_id, 'user_id': target_id}}
)

# 2. Update predictions
res2 = db_client.db.predictions.update_many(
    {'patient_name': patient_name},
    {'$set': {'patient_id': target_id, 'user_id': target_id}}
)

print(f"Done. Modified {res1.modified_count} medical records and {res2.modified_count} predictions.")

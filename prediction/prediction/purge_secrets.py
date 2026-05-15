"""
Security Remediation Script
============================
1. Removes hardcoded credentials from all utility/scratch scripts
2. Replaces them with os.environ.get() calls
"""

import os
import re

TARGET_DIR = "."

# The hardcoded strings we need to purge
MONGO_HARDCODED = 'mongodb+srv://ashishking554_db_user:Azziizz%4014@diseasepredictionvalida.dlayq9m.mongodb.net/?appName=DiseasePredictionValidation'
MONGO_SAFE = 'os.environ.get("MONGO_URI", "")'

# Files with direct pymongo.MongoClient("hardcoded...")
FILES_TO_FIX = [
    "backend/assign_doctor.py",
    "backend/check_patients_db.py",
    "backend/debug_mongo.py",
    "backend/test_flag_logic.py",
]

def fix_file(filepath):
    if not os.path.exists(filepath):
        print(f"  SKIP (not found): {filepath}")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Replace hardcoded mongo URIs
    content = content.replace(f'"{MONGO_HARDCODED}"', MONGO_SAFE)
    content = content.replace(f"'{MONGO_HARDCODED}'", MONGO_SAFE)

    # Add os import if not present
    if 'os.environ' in content and 'import os' not in content:
        content = "import os\n" + content

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  FIXED: {filepath}")
    else:
        print(f"  UNCHANGED: {filepath}")

print("=== Purging hardcoded credentials from committed scripts ===\n")
for f in FILES_TO_FIX:
    fix_file(f)
print("\nDone.")

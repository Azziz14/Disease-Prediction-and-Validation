import os
from app import app

print("Listing all registered routes:")
for rule in app.url_map.iter_rules():
    print(f"{rule.endpoint}: {rule}")

import datetime
from utils.db import db_client

def send_clinical_email(to_email, from_email, subject, body_text):
    """
    Simulated Clinical Mail Protocol (SMTP-Emulator).
    Records and logs outgoing mail packets targeting custom/mock domains like @carepredict.ai
    without requiring live authenticated internet postmasters.
    """
    timestamp = datetime.datetime.utcnow().isoformat()
    
    # Construct Standard SMTP Protocol Payload Structure
    email_record = {
        "to": to_email,
        "from": from_email,
        "subject": subject,
        "body": body_text,
        "protocol": "SMTP-Mock (carepredict.ai)",
        "status": "DISPATCHED_SUCCESSFULLY",
        "timestamp": timestamp
    }
    
    # 1. Persistence Layer: Inject to clinical database outbox
    try:
        if db_client.db is not None:
            db_client.db.clinical_outbox.insert_one(email_record)
    except Exception as e:
        print(f"[SMTP ERR] Failed to write to MongoDB spooler: {str(e)}")

    # 2. Diagnostics Layer: Render a beautiful ASCII diagnostic block in terminal
    border = "=" * 60
    print(f"\n{border}")
    print(f"🔒 [SMTP EMULATOR] OUTGOING CLINICAL MAIL DISPATCHED")
    print(f"📅 Timestamp : {timestamp}")
    print(f"📤 From      : {from_email}")
    print(f"📥 To        : {to_email}")
    print(f"📑 Subject   : {subject}")
    print(f"{'-' * 60}")
    print(f"📝 Body Content:")
    print(f"   {body_text}")
    print(f"{border}\n")
    
    return True

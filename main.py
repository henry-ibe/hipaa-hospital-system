
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename='/var/log/hospital-audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def log_access(username: str, role: str, endpoint: str, patient_id: str = None):
    logging.info(f"USER={username} ROLE={role} ENDPOINT={endpoint} PATIENT={patient_id}")

# Update patients endpoint to log access
@app.get("/patients/{patient_id}", dependencies=[Depends(require_role("doctor"))])
def get_patient(patient_id: str, token_data: dict = Depends(verify_token)):
    log_access(token_data["username"], token_data["role"], f"/patients/{patient_id}", patient_id)
    return {"patient_id": patient_id, "name": "John Doe", "status": "stable"}

import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename='/var/log/hospital-audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def log_access(username: str, role: str, endpoint: str, patient_id: str = None):
    logging.info(f"USER={username} ROLE={role} ENDPOINT={endpoint} PATIENT={patient_id}")

# Update patients endpoint to log access
@app.get("/patients/{patient_id}", dependencies=[Depends(require_role("doctor"))])
def get_patient(patient_id: str, token_data: dict = Depends(verify_token)):
    log_access(token_data["username"], token_data["role"], f"/patients/{patient_id}", patient_id)
    return {"patient_id": patient_id, "name": "John Doe", "status": "stable"}

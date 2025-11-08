from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import pyotp
import jwt
from datetime import datetime, timedelta

app = FastAPI()
security = HTTPBearer()

SECRET_KEY = "your-secret-key-change-in-production"
USERS = {
    "doctor": {"password": "demo123", "role": "doctor", "mfa_secret": "JBSWY3DPEHPK3PXP"},
    "nurse": {"password": "demo123", "role": "nurse", "mfa_secret": "JBSWY3DPEHPK3PXP"},
    "admin": {"password": "demo123", "role": "admin", "mfa_secret": "JBSWY3DPEHPK3PXP"}
}

def create_token(username: str, role: str):
    payload = {
        "username": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload
    except:
        raise HTTPException(401, "Invalid token")

def require_role(required_role: str):
    def role_checker(token_data: dict = Depends(verify_token)):
        if token_data["role"] != required_role:
            raise HTTPException(403, f"Requires {required_role} role")
        return token_data
    return role_checker

@app.get("/")
def root():
    return {"hospital": "Mount Sinai", "location": "NY", "status": "secure"}

@app.post("/login")
def login(username: str, password: str):
    user = USERS.get(username)
    if user and user["password"] == password:
        return {"status": "mfa_required", "username": username}
    raise HTTPException(401, "Invalid credentials")

@app.post("/mfa/verify")
def verify_mfa(username: str, code: str):
    user = USERS.get(username)
    if not user:
        raise HTTPException(401, "Invalid user")
    
    totp = pyotp.TOTP(user["mfa_secret"])
    if totp.verify(code):
        token = create_token(username, user["role"])
        return {"access_token": token, "role": user["role"]}
    raise HTTPException(401, "Invalid MFA")

# Doctor-only endpoint
@app.get("/patients", dependencies=[Depends(require_role("doctor"))])
def get_patients():
    return {"patients": ["John Doe", "Jane Smith"]}

# Nurse-only endpoint
@app.get("/vitals", dependencies=[Depends(require_role("nurse"))])
def get_vitals():
    return {"vitals": "Temperature, BP, Pulse"}

# Admin-only endpoint
@app.get("/admin/users", dependencies=[Depends(require_role("admin"))])
def get_users():
    return {"users": list(USERS.keys())}

import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename='/home/ec2-user/hospital-audit.log',
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

# In-memory database for demo
appointments_db = []

@app.post("/appointments")
def create_appointment(
    patient_name: str,
    doctor_name: str,
    date: str,
    time: str,
    token_data: dict = Depends(verify_token)
):
    # Only doctors and nurses can create appointments
    if token_data["role"] not in ["doctor", "nurse", "admin"]:
        raise HTTPException(403, "Requires doctor/nurse/admin role")
    
    appointment = {
        "id": len(appointments_db) + 1,
        "patient_name": patient_name,
        "doctor_name": doctor_name,
        "date": date,
        "time": time,
        "created_by": token_data["username"]
    }
    appointments_db.append(appointment)
    
    # Audit log
    log_access(token_data["username"], token_data["role"], "/appointments POST", patient_name)
    
    return {"status": "created", "appointment": appointment}

@app.get("/appointments")
def list_appointments(token_data: dict = Depends(verify_token)):
    # All authenticated users can view appointments
    log_access(token_data["username"], token_data["role"], "/appointments GET", None)
    return {"appointments": appointments_db}

@app.delete("/appointments/{appointment_id}")
def cancel_appointment(
    appointment_id: int,
    token_data: dict = Depends(verify_token)
):
    # Only doctors and admins can cancel
    if token_data["role"] not in ["doctor", "admin"]:
        raise HTTPException(403, "Requires doctor/admin role")
    
    # Find and remove appointment
    for apt in appointments_db:
        if apt["id"] == appointment_id:
            appointments_db.remove(apt)
            log_access(token_data["username"], token_data["role"], f"/appointments DELETE {appointment_id}", apt["patient_name"])
            return {"status": "cancelled", "appointment": apt}
    
    raise HTTPException(404, "Appointment not found")

prescriptions_db = []

@app.post("/prescriptions", dependencies=[Depends(require_role("doctor"))])
def write_prescription(
    patient_name: str,
    medication: str,
    dosage: str,
    duration: str,
    token_data: dict = Depends(verify_token)
):
    prescription = {
        "id": len(prescriptions_db) + 1,
        "patient_name": patient_name,
        "medication": medication,
        "dosage": dosage,
        "duration": duration,
        "prescribed_by": token_data["username"],
        "date": "2025-11-08"
    }
    prescriptions_db.append(prescription)
    log_access(token_data["username"], token_data["role"], "/prescriptions POST", patient_name)
    return {"status": "prescribed", "prescription": prescription}

@app.get("/prescriptions")
def view_prescriptions(token_data: dict = Depends(verify_token)):
    log_access(token_data["username"], token_data["role"], "/prescriptions GET", None)
    return {"prescriptions": prescriptions_db}

billing_db = []

@app.post("/billing", dependencies=[Depends(require_role("admin"))])
def create_invoice(
    patient_name: str,
    service: str,
    amount: float,
    insurance: str,
    token_data: dict = Depends(verify_token)
):
    invoice = {
        "id": len(billing_db) + 1,
        "patient_name": patient_name,
        "service": service,
        "amount": amount,
        "insurance": insurance,
        "created_by": token_data["username"],
        "date": "2025-11-08",
        "status": "pending"
    }
    billing_db.append(invoice)
    log_access(token_data["username"], token_data["role"], "/billing POST", patient_name)
    return {"status": "invoice_created", "invoice": invoice}

@app.get("/billing")
def view_invoices(token_data: dict = Depends(verify_token)):
    # Only admin and billing roles can view
    if token_data["role"] not in ["admin"]:
        raise HTTPException(403, "Requires admin role")
    log_access(token_data["username"], token_data["role"], "/billing GET", None)
    return {"invoices": billing_db}

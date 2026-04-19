import os
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
    AUTH_ATTEMPTS.labels(status="success", region=REGION, hospital=HOSPITAL).inc()
    if user and user["password"] == password:
        return {"status": "mfa_required", "username": username}
    AUTH_ATTEMPTS.labels(status="failed", region=REGION, hospital=HOSPITAL).inc()
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
    PRESCRIPTIONS_WRITTEN.labels(medication_type=medication, region=REGION, hospital=HOSPITAL).inc()
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
    BILLING_TRANSACTIONS.labels(status="success", region=REGION, hospital=HOSPITAL).inc()
    BILLING_AMOUNT.labels(region=REGION, hospital=HOSPITAL).inc(amount)
    log_access(token_data["username"], token_data["role"], "/billing POST", patient_name)
    return {"status": "invoice_created", "invoice": invoice}

@app.get("/billing")
def view_invoices(token_data: dict = Depends(verify_token)):
    # Only admin and billing roles can view
    if token_data["role"] not in ["admin"]:
        raise HTTPException(403, "Requires admin role")
    log_access(token_data["username"], token_data["role"], "/billing GET", None)
    return {"invoices": billing_db}

# ── Observability endpoints ──────────────────────────────────────────
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time

REQUEST_COUNT = Counter(
    'hospital_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status', 'region', 'hospital']
)

REQUEST_LATENCY = Histogram(
    'hospital_request_duration_seconds',
    'Request latency',
    ['endpoint', 'region', 'hospital']
)

BED_OCCUPANCY = Gauge(
    'hospital_bed_occupancy_ratio',
    'Bed occupancy by department',
    ['department', 'region', 'hospital']
)

REGION = os.getenv("HOSPITAL_REGION", "unknown")
HOSPITAL = os.getenv("HOSPITAL_NAME", "unknown")

# Seed some bed occupancy metrics
BED_OCCUPANCY.labels(department="emergency", region=REGION, hospital=HOSPITAL).set(0.87)
BED_OCCUPANCY.labels(department="icu", region=REGION, hospital=HOSPITAL).set(0.92)
BED_OCCUPANCY.labels(department="general", region=REGION, hospital=HOSPITAL).set(0.65)

@app.get("/health")
def health():
    return {"status": "healthy", "region": REGION, "hospital": HOSPITAL}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# ── Extended Business Metrics ────────────────────────────────────────

# Patient metrics
PATIENT_ADMISSIONS = Counter(
    'hospital_patient_admissions_total',
    'Total patient admissions',
    ['department', 'region', 'hospital']
)

PATIENT_WAIT_TIME = Histogram(
    'hospital_patient_wait_seconds',
    'Patient wait time in seconds',
    ['department', 'region', 'hospital'],
    buckets=[300, 600, 900, 1800, 3600, 7200]
)

PATIENTS_ACTIVE = Gauge(
    'hospital_patients_active',
    'Currently active patients',
    ['department', 'region', 'hospital']
)

# API performance
API_REQUEST_COUNT = Counter(
    'hospital_api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status_code', 'region', 'hospital']
)

API_LATENCY = Histogram(
    'hospital_api_duration_seconds',
    'API request duration',
    ['endpoint', 'region', 'hospital'],
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0]
)

# Appointment metrics
APPOINTMENTS_BOOKED = Counter(
    'hospital_appointments_booked_total',
    'Total appointments booked',
    ['department', 'region', 'hospital']
)

APPOINTMENTS_CANCELLED = Counter(
    'hospital_appointments_cancelled_total',
    'Total appointments cancelled',
    ['department', 'region', 'hospital']
)

# Billing metrics
BILLING_TRANSACTIONS = Counter(
    'hospital_billing_transactions_total',
    'Total billing transactions',
    ['status', 'region', 'hospital']
)

BILLING_AMOUNT = Counter(
    'hospital_billing_amount_dollars_total',
    'Total billing amount in dollars',
    ['region', 'hospital']
)

# Prescription metrics
PRESCRIPTIONS_WRITTEN = Counter(
    'hospital_prescriptions_written_total',
    'Total prescriptions written',
    ['medication_type', 'region', 'hospital']
)

# Auth metrics
AUTH_ATTEMPTS = Counter(
    'hospital_auth_attempts_total',
    'Total authentication attempts',
    ['status', 'region', 'hospital']
)

MFA_FAILURES = Counter(
    'hospital_mfa_failures_total',
    'Total MFA verification failures',
    ['region', 'hospital']
)

# Database metrics
DB_QUERY_LATENCY = Histogram(
    'hospital_db_query_seconds',
    'Database query duration',
    ['query_type', 'region', 'hospital'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

DB_CONNECTION_POOL = Gauge(
    'hospital_db_connection_pool_usage',
    'DB connection pool usage ratio',
    ['region', 'hospital']
)

# Seed realistic initial values
import random

# Active patients per department
PATIENTS_ACTIVE.labels(department="emergency", region=REGION, hospital=HOSPITAL).set(random.randint(18, 35))
PATIENTS_ACTIVE.labels(department="icu", region=REGION, hospital=HOSPITAL).set(random.randint(8, 15))
PATIENTS_ACTIVE.labels(department="general", region=REGION, hospital=HOSPITAL).set(random.randint(45, 80))
PATIENTS_ACTIVE.labels(department="surgery", region=REGION, hospital=HOSPITAL).set(random.randint(5, 12))

# DB connection pool
DB_CONNECTION_POOL.labels(region=REGION, hospital=HOSPITAL).set(round(random.uniform(0.3, 0.7), 2))

# Middleware to track every API request automatically
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start

        API_REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            region=REGION,
            hospital=HOSPITAL
        ).inc()

        API_LATENCY.labels(
            endpoint=request.url.path,
            region=REGION,
            hospital=HOSPITAL
        ).observe(duration)

        return response

app.add_middleware(MetricsMiddleware)

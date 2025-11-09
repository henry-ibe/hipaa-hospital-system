from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import pyotp
import jwt
from datetime import datetime, timedelta
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time
from typing import Optional
import json

app = FastAPI(title="Mount Sinai Hospital Management System")
security = HTTPBearer()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

SECRET_KEY = "your-secret-key-change-in-production"

# Prometheus Metrics
request_count = Counter('hospital_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
login_attempts = Counter('hospital_login_attempts', 'Login attempts', ['status'])
mfa_attempts = Counter('hospital_mfa_attempts', 'MFA verification attempts', ['status'])
response_time = Histogram('hospital_response_seconds', 'Response time', ['endpoint'])
active_sessions = Gauge('hospital_active_sessions', 'Active user sessions')

# User Database (in production, use PostgreSQL)
USERS = {
    "dr.smith": {
        "password": "doctor123",
        "role": "doctor",
        "name": "Dr. Sarah Smith",
        "department": "Cardiology",
        "mfa_secret": "JBSWY3DPEHPK3PXP"
    },
    "nurse.johnson": {
        "password": "nurse123",
        "role": "nurse",
        "name": "Emily Johnson",
        "department": "Emergency",
        "mfa_secret": "JBSWY3DPEHPK3PXP"
    },
    "admin": {
        "password": "admin123",
        "role": "admin",
        "name": "Michael Chen",
        "department": "Administration",
        "mfa_secret": "JBSWY3DPEHPK3PXP"
    },
    "billing.davis": {
        "password": "billing123",
        "role": "billing",
        "name": "Jessica Davis",
        "department": "Finance",
        "mfa_secret": "JBSWY3DPEHPK3PXP"
    },
    "lab.wilson": {
        "password": "lab123",
        "role": "lab",
        "name": "Robert Wilson",
        "department": "Laboratory",
        "mfa_secret": "JBSWY3DPEHPK3PXP"
    },
    "reception.brown": {
        "password": "reception123",
        "role": "receptionist",
        "name": "Lisa Brown",
        "department": "Front Desk",
        "mfa_secret": "JBSWY3DPEHPK3PXP"
    }
}

# Mock Patient Data
PATIENTS = [
    {
        "id": "P001",
        "name": "John Anderson",
        "age": 45,
        "gender": "Male",
        "blood_type": "O+",
        "condition": "Hypertension",
        "room": "204A",
        "doctor": "Dr. Sarah Smith",
        "admitted": "2025-11-05",
        "vitals": {
            "bp": "140/90",
            "heart_rate": 78,
            "temp": 98.6,
            "oxygen": 97
        },
        "medications": ["Lisinopril 10mg", "Aspirin 81mg"],
        "allergies": ["Penicillin"],
        "insurance": "Blue Cross PPO",
        "balance": 2500.00
    },
    {
        "id": "P002",
        "name": "Maria Garcia",
        "age": 32,
        "gender": "Female",
        "blood_type": "A+",
        "condition": "Diabetes Type 2",
        "room": "305B",
        "doctor": "Dr. Sarah Smith",
        "admitted": "2025-11-06",
        "vitals": {
            "bp": "125/85",
            "heart_rate": 72,
            "temp": 98.4,
            "oxygen": 98
        },
        "medications": ["Metformin 500mg", "Insulin"],
        "allergies": ["None"],
        "insurance": "Aetna HMO",
        "balance": 1200.00
    },
    {
        "id": "P003",
        "name": "James Wilson",
        "age": 67,
        "gender": "Male",
        "blood_type": "B-",
        "condition": "Post-Surgery Recovery",
        "room": "401C",
        "doctor": "Dr. Sarah Smith",
        "admitted": "2025-11-02",
        "vitals": {
            "bp": "130/88",
            "heart_rate": 65,
            "temp": 99.1,
            "oxygen": 96
        },
        "medications": ["Morphine", "Antibiotics"],
        "allergies": ["Latex"],
        "insurance": "Medicare",
        "balance": 8500.00
    },
    {
        "id": "P004",
        "name": "Sarah Thompson",
        "age": 28,
        "gender": "Female",
        "blood_type": "AB+",
        "condition": "Pregnancy - Third Trimester",
        "room": "210A",
        "doctor": "Dr. Sarah Smith",
        "admitted": "2025-11-07",
        "vitals": {
            "bp": "118/75",
            "heart_rate": 82,
            "temp": 98.2,
            "oxygen": 99
        },
        "medications": ["Prenatal Vitamins"],
        "allergies": ["Sulfa drugs"],
        "insurance": "United Healthcare",
        "balance": 450.00
    },
    {
        "id": "P005",
        "name": "Robert Lee",
        "age": 55,
        "gender": "Male",
        "blood_type": "O-",
        "condition": "Pneumonia",
        "room": "308D",
        "doctor": "Dr. Sarah Smith",
        "admitted": "2025-11-08",
        "vitals": {
            "bp": "135/92",
            "heart_rate": 88,
            "temp": 100.4,
            "oxygen": 94
        },
        "medications": ["Azithromycin", "Albuterol"],
        "allergies": ["Shellfish"],
        "insurance": "Cigna PPO",
        "balance": 3200.00
    }
]

# Lab Test Orders
LAB_ORDERS = [
    {
        "id": "L001",
        "patient_id": "P001",
        "patient_name": "John Anderson",
        "test_type": "Complete Blood Count",
        "ordered_by": "Dr. Sarah Smith",
        "status": "Pending",
        "priority": "Routine",
        "ordered_date": "2025-11-08 08:30",
        "sample_type": "Blood"
    },
    {
        "id": "L002",
        "patient_id": "P002",
        "patient_name": "Maria Garcia",
        "test_type": "HbA1c",
        "ordered_by": "Dr. Sarah Smith",
        "status": "In Progress",
        "priority": "Routine",
        "ordered_date": "2025-11-08 09:15",
        "sample_type": "Blood"
    },
    {
        "id": "L003",
        "patient_id": "P005",
        "patient_name": "Robert Lee",
        "test_type": "Chest X-Ray",
        "ordered_by": "Dr. Sarah Smith",
        "status": "Pending",
        "priority": "Urgent",
        "ordered_date": "2025-11-08 10:00",
        "sample_type": "Imaging"
    },
    {
        "id": "L004",
        "patient_id": "P003",
        "patient_name": "James Wilson",
        "test_type": "Wound Culture",
        "ordered_by": "Dr. Sarah Smith",
        "status": "Completed",
        "priority": "Stat",
        "ordered_date": "2025-11-07 14:20",
        "sample_type": "Swab",
        "results": "Negative for infection"
    }
]

# Appointments
APPOINTMENTS = [
    {
        "id": "A001",
        "patient_name": "Emma Davis",
        "time": "09:00 AM",
        "date": "2025-11-08",
        "doctor": "Dr. Sarah Smith",
        "type": "Follow-up",
        "status": "Scheduled"
    },
    {
        "id": "A002",
        "patient_name": "Michael Brown",
        "time": "10:30 AM",
        "date": "2025-11-08",
        "doctor": "Dr. Sarah Smith",
        "type": "New Patient",
        "status": "Checked In"
    },
    {
        "id": "A003",
        "patient_name": "Jennifer White",
        "time": "02:00 PM",
        "date": "2025-11-08",
        "doctor": "Dr. Sarah Smith",
        "type": "Consultation",
        "status": "Scheduled"
    }
]

# Billing Invoices
INVOICES = [
    {
        "id": "INV001",
        "patient_id": "P001",
        "patient_name": "John Anderson",
        "date": "2025-11-08",
        "services": [
            {"name": "Room Charge", "amount": 1500.00},
            {"name": "Consultation", "amount": 250.00},
            {"name": "Medications", "amount": 750.00}
        ],
        "total": 2500.00,
        "insurance_paid": 0.00,
        "patient_balance": 2500.00,
        "status": "Pending"
    },
    {
        "id": "INV002",
        "patient_id": "P002",
        "patient_name": "Maria Garcia",
        "date": "2025-11-07",
        "services": [
            {"name": "Lab Tests", "amount": 450.00},
            {"name": "Consultation", "amount": 250.00},
            {"name": "Medications", "amount": 500.00}
        ],
        "total": 1200.00,
        "insurance_paid": 0.00,
        "patient_balance": 1200.00,
        "status": "Pending"
    },
    {
        "id": "INV003",
        "patient_id": "P003",
        "patient_name": "James Wilson",
        "date": "2025-11-02",
        "services": [
            {"name": "Surgery", "amount": 5000.00},
            {"name": "ICU Stay (3 days)", "amount": 3000.00},
            {"name": "Medications", "amount": 500.00}
        ],
        "total": 8500.00,
        "insurance_paid": 6000.00,
        "patient_balance": 2500.00,
        "status": "Partially Paid"
    }
]

def create_token(username: str, role: str):
    payload = {
        "username": username,
        "role": role,
        "name": USERS[username]["name"],
        "department": USERS[username]["department"],
        "exp": datetime.utcnow() + timedelta(hours=8)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload
    except:
        raise HTTPException(401, "Invalid token")

# ============== HTML PAGES ==============

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """Hospital landing page"""
    request_count.labels(method='GET', endpoint='/', status='200').inc()
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard/{role}", response_class=HTMLResponse)
async def dashboard_page(request: Request, role: str):
    """Role-based dashboard pages"""
    valid_roles = ["doctor", "nurse", "admin", "billing", "lab", "receptionist"]
    if role not in valid_roles:
        raise HTTPException(404, "Invalid role")
    
    template_map = {
        "doctor": "doctor.html",
        "nurse": "nurse.html",
        "admin": "admin.html",
        "billing": "billing.html",
        "lab": "lab.html",
        "receptionist": "receptionist.html"
    }
    
    return templates.TemplateResponse(template_map[role], {"request": request})

# ============== AUTH API ==============

@app.post("/api/auth/login")
async def api_login(username: str, password: str):
    """Step 1: Username/Password authentication"""
    start_time = time.time()
    try:
        if username not in USERS or USERS[username]["password"] != password:
            login_attempts.labels(status='failed').inc()
            request_count.labels(method='POST', endpoint='/api/auth/login', status='401').inc()
            response_time.labels(endpoint='/api/auth/login').observe(time.time() - start_time)
            raise HTTPException(401, "Invalid credentials")
        
        login_attempts.labels(status='success').inc()
        request_count.labels(method='POST', endpoint='/api/auth/login', status='200').inc()
        response_time.labels(endpoint='/api/auth/login').observe(time.time() - start_time)
        
        return {
            "success": True,
            "message": "Credentials valid, MFA required",
            "username": username,
            "role": USERS[username]["role"],
            "name": USERS[username]["name"],
            "mfa_required": True
        }
    except HTTPException:
        response_time.labels(endpoint='/api/auth/login').observe(time.time() - start_time)
        raise

@app.post("/api/auth/mfa")
async def api_mfa_verify(username: str, mfa_code: str):
    """Step 2: MFA verification"""
    start_time = time.time()
    try:
        if username not in USERS:
            mfa_attempts.labels(status='invalid_user').inc()
            request_count.labels(method='POST', endpoint='/api/auth/mfa', status='401').inc()
            raise HTTPException(401, "Invalid user")
        
        totp = pyotp.TOTP(USERS[username]["mfa_secret"])
        
        if not totp.verify(mfa_code, valid_window=1):
            mfa_attempts.labels(status='failed').inc()
            request_count.labels(method='POST', endpoint='/api/auth/mfa', status='401').inc()
            raise HTTPException(401, "Invalid MFA code")
        
        mfa_attempts.labels(status='success').inc()
        active_sessions.inc()
        token = create_token(username, USERS[username]["role"])
        
        request_count.labels(method='POST', endpoint='/api/auth/mfa', status='200').inc()
        response_time.labels(endpoint='/api/auth/mfa').observe(time.time() - start_time)
        
        return {
            "success": True,
            "access_token": token,
            "token_type": "bearer",
            "role": USERS[username]["role"],
            "name": USERS[username]["name"],
            "department": USERS[username]["department"]
        }
    except HTTPException:
        response_time.labels(endpoint='/api/auth/mfa').observe(time.time() - start_time)
        raise

# ============== DOCTOR API ==============

@app.get("/api/doctor/patients")
async def get_patients(user=Depends(verify_token)):
    """Get patient list for doctor"""
    if user['role'] not in ['doctor', 'nurse', 'admin']:
        raise HTTPException(403, "Access denied")
    return {"patients": PATIENTS}

@app.get("/api/doctor/patient/{patient_id}")
async def get_patient_details(patient_id: str, user=Depends(verify_token)):
    """Get detailed patient information"""
    if user['role'] not in ['doctor', 'nurse', 'admin']:
        raise HTTPException(403, "Access denied")
    
    patient = next((p for p in PATIENTS if p['id'] == patient_id), None)
    if not patient:
        raise HTTPException(404, "Patient not found")
    return patient

@app.post("/api/doctor/prescribe")
async def prescribe_medication(patient_id: str, medication: str, user=Depends(verify_token)):
    """Prescribe medication to patient"""
    if user['role'] != 'doctor':
        raise HTTPException(403, "Only doctors can prescribe")
    
    return {
        "success": True,
        "message": f"Prescribed {medication} to patient {patient_id}",
        "prescribed_by": user['name']
    }

# ============== NURSE API ==============

@app.get("/api/nurse/vitals/{patient_id}")
async def get_patient_vitals(patient_id: str, user=Depends(verify_token)):
    """Get patient vital signs"""
    if user['role'] not in ['nurse', 'doctor', 'admin']:
        raise HTTPException(403, "Access denied")
    
    patient = next((p for p in PATIENTS if p['id'] == patient_id), None)
    if not patient:
        raise HTTPException(404, "Patient not found")
    
    return {
        "patient_id": patient_id,
        "patient_name": patient['name'],
        "vitals": patient['vitals'],
        "last_updated": datetime.now().isoformat()
    }

@app.post("/api/nurse/vitals/update")
async def update_vitals(patient_id: str, vitals: dict, user=Depends(verify_token)):
    """Update patient vitals"""
    if user['role'] not in ['nurse', 'doctor']:
        raise HTTPException(403, "Access denied")
    
    return {
        "success": True,
        "message": f"Vitals updated for patient {patient_id}",
        "updated_by": user['name']
    }

# ============== LAB API ==============

@app.get("/api/lab/orders")
async def get_lab_orders(user=Depends(verify_token)):
    """Get pending lab test orders"""
    if user['role'] not in ['lab', 'doctor', 'admin']:
        raise HTTPException(403, "Access denied")
    return {"orders": LAB_ORDERS}

@app.post("/api/lab/results")
async def submit_lab_results(order_id: str, results: str, user=Depends(verify_token)):
    """Submit lab test results"""
    if user['role'] != 'lab':
        raise HTTPException(403, "Only lab technicians can submit results")
    
    return {
        "success": True,
        "message": f"Results submitted for order {order_id}",
        "submitted_by": user['name']
    }

# ============== BILLING API ==============

@app.get("/api/billing/invoices")
async def get_invoices(user=Depends(verify_token)):
    """Get all billing invoices"""
    if user['role'] not in ['billing', 'admin']:
        raise HTTPException(403, "Access denied")
    return {"invoices": INVOICES}

@app.get("/api/billing/invoice/{invoice_id}")
async def get_invoice_details(invoice_id: str, user=Depends(verify_token)):
    """Get detailed invoice information"""
    if user['role'] not in ['billing', 'admin']:
        raise HTTPException(403, "Access denied")
    
    invoice = next((inv for inv in INVOICES if inv['id'] == invoice_id), None)
    if not invoice:
        raise HTTPException(404, "Invoice not found")
    return invoice

@app.post("/api/billing/payment")
async def process_payment(invoice_id: str, amount: float, user=Depends(verify_token)):
    """Process patient payment"""
    if user['role'] != 'billing':
        raise HTTPException(403, "Only billing staff can process payments")
    
    return {
        "success": True,
        "message": f"Payment of ${amount} processed for invoice {invoice_id}",
        "processed_by": user['name']
    }

# ============== RECEPTIONIST API ==============

@app.get("/api/reception/appointments")
async def get_appointments(user=Depends(verify_token)):
    """Get today's appointments"""
    if user['role'] not in ['receptionist', 'doctor', 'admin']:
        raise HTTPException(403, "Access denied")
    return {"appointments": APPOINTMENTS}

@app.post("/api/reception/checkin")
async def checkin_patient(appointment_id: str, user=Depends(verify_token)):
    """Check in a patient"""
    if user['role'] != 'receptionist':
        raise HTTPException(403, "Only reception can check in patients")
    
    return {
        "success": True,
        "message": f"Patient checked in for appointment {appointment_id}",
        "checked_in_by": user['name']
    }

# ============== ADMIN API ==============

@app.get("/api/admin/incidents")
async def get_security_incidents(user=Depends(verify_token)):
    """Get security incidents from incident responder"""
    if user['role'] != 'admin':
        raise HTTPException(403, "Admin access required")
    
    try:
        with open('/home/ec2-user/hospital-app/incident-response/incidents.log', 'r') as f:
            incidents = [json.loads(line) for line in f.readlines()]
        return {"incidents": incidents[-10:]}  # Last 10 incidents
    except:
        return {"incidents": []}

@app.get("/api/admin/stats")
async def get_system_stats(user=Depends(verify_token)):
    """Get system statistics"""
    if user['role'] != 'admin':
        raise HTTPException(403, "Admin access required")
    
    return {
        "total_patients": len(PATIENTS),
        "active_users": len(USERS),
        "pending_lab_orders": len([o for o in LAB_ORDERS if o['status'] == 'Pending']),
        "total_invoices": len(INVOICES),
        "total_revenue": sum(inv['total'] for inv in INVOICES),
        "appointments_today": len(APPOINTMENTS)
    }

# ============== MONITORING ==============

@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
def health():
    """Health check endpoint"""
    request_count.labels(method='GET', endpoint='/health', status='200').inc()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Mount Sinai Hospital Management System"
    }

@app.get("/api/test-credentials")
def test_credentials():
    """Display test login credentials"""
    creds = {}
    for username, data in USERS.items():
        creds[username] = {
            "username": username,
            "password": data["password"],
            "role": data["role"],
            "name": data["name"],
            "mfa_code": "Use Google Authenticator with secret: JBSWY3DPEHPK3PXP"
        }
    return {"test_accounts": creds}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)

# Add this import at the top if not already there
from fastapi.responses import StreamingResponse
import io

@app.get("/mfa-setup", response_class=HTMLResponse)
async def mfa_setup_page(request: Request):
    """MFA Setup page"""
    return templates.TemplateResponse("mfa-setup.html", {"request": request})

@app.get("/api/auth/mfa-qr/{username}")
async def get_mfa_qr(username: str):
    """Generate QR code for user MFA setup"""
    if username not in USERS:
        raise HTTPException(404, "User not found")
    
    try:
        import qrcode
        from io import BytesIO
        
        # Generate TOTP provisioning URI
        secret = USERS[username]["mfa_secret"]
        name = USERS[username]["name"]
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(
            name=f"{username}",
            issuer_name="Mount Sinai Hospital"
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        
        return StreamingResponse(buf, media_type="image/png")
    except ImportError:
        raise HTTPException(500, "QR code library not installed")

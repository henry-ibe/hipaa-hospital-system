import requests
import random
import time
import pyotp

BASE_URL = "http://localhost:8000"
MFA_SECRET = "JBSWY3DPEHPK3PXP"

def get_token(username, password):
    try:
        requests.post(f"{BASE_URL}/login?username={username}&password={password}")
        code = pyotp.TOTP(MFA_SECRET).now()
        r = requests.post(f"{BASE_URL}/mfa/verify?username={username}&code={code}")
        return r.json().get("access_token")
    except:
        return None

def simulate():
    print("Starting traffic simulator...")
    while True:
        try:
            # Health checks
            requests.get(f"{BASE_URL}/health")
            requests.get(f"{BASE_URL}/metrics")

            # Auth traffic
            requests.post(f"{BASE_URL}/login?username=doctor&password=demo123")
            requests.post(f"{BASE_URL}/login?username=nurse&password=demo123")
            requests.post(f"{BASE_URL}/login?username=doctor&password=wrongpass")

            # Get tokens
            admin_token  = get_token("admin", "demo123")
            doctor_token = get_token("doctor", "demo123")

            if admin_token:
                headers = {"Authorization": f"Bearer {admin_token}"}

                # Billing transactions
                for i in range(random.randint(2, 5)):
                    requests.post(
                        f"{BASE_URL}/billing",
                        params={
                            "patient_name": f"Patient{random.randint(1,100)}",
                            "service": random.choice(["consultation","surgery","imaging","lab"]),
                            "amount": random.randint(100, 5000),
                            "insurance": random.choice(["BlueCross","Aetna","Medicare","self-pay"])
                        },
                        headers=headers
                    )

                # View invoices
                requests.get(f"{BASE_URL}/billing", headers=headers)

            if doctor_token:
                headers = {"Authorization": f"Bearer {doctor_token}"}

                # Prescriptions
                for i in range(random.randint(1, 3)):
                    requests.post(
                        f"{BASE_URL}/prescriptions",
                        params={
                            "patient_name": f"Patient{random.randint(1,100)}",
                            "medication": random.choice(["antibiotic","painkiller","cardiac","diabetes","antibiotic"]),
                            "dosage": random.choice(["500mg","250mg","10mg","100mg"]),
                            "duration": random.choice(["7days","14days","30days"])
                        },
                        headers=headers
                    )

                # View patients
                requests.get(f"{BASE_URL}/patients", headers=headers)

            print(f"Traffic sent at {time.strftime('%H:%M:%S')}")
            time.sleep(30)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

simulate()

from fastapi import FastAPI, Request
from dotenv import load_dotenv
import anthropic
import requests
import os

load_dotenv()

client      = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
NTFY_URL    = "https://ntfy.sh/henry-hospital-sro"
SN_INSTANCE = os.environ["SN_INSTANCE"]
SN_USER     = os.environ["SN_USER"]
SN_PASSWORD = os.environ["SN_PASSWORD"]
SN_URL      = f"https://{SN_INSTANCE}/api/now/table/incident"

# Tracks fingerprint -> sys_id for auto-resolve
incident_map = {}

app = FastAPI()

def create_servicenow_incident(name, severity, region, hospital, triage):
    priority = "1" if severity == "critical" else "2"
    payload = {
        "short_description": f"[{region.upper()}/{hospital}] {name} - AI Triaged",
        "description": f"=== AI TRIAGE (Claude) ===\n\n{triage}\n\n=== ALERT INFO ===\nAlert: {name}\nSeverity: {severity}\nRegion: {region}\nHospital: {hospital}",
        "category": "Infrastructure",
        "priority": priority,
        "urgency": priority,
    }
    r = requests.post(
        SN_URL,
        json=payload,
        auth=(SN_USER, SN_PASSWORD),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        timeout=15
    )
    r.raise_for_status()
    result = r.json()["result"]
    return result["number"], result["sys_id"]

def resolve_servicenow_incident(sys_id, name):
    r = requests.patch(
        f"{SN_URL}/{sys_id}",
        json={
            "state": "6",
            "close_code": "Solved (Permanently)",
            "close_notes": f"Alert '{name}' resolved automatically by AI Triage Agent."
        },
        auth=(SN_USER, SN_PASSWORD),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        timeout=15
    )
    r.raise_for_status()
    print(f"[SERVICENOW] Incident {sys_id} resolved.")

@app.post("/webhook")
async def receive_alert(request: Request):
    payload = await request.json()
    alerts  = payload.get("alerts", [])
    for alert in alerts:
        name        = alert["labels"].get("alertname", "Unknown")
        status      = alert.get("status", "unknown")
        severity    = alert["labels"].get("severity", "unknown")
        region      = alert["labels"].get("region", "unknown")
        hospital    = alert["labels"].get("hospital", "unknown")
        description = alert.get("annotations", {}).get("description", "No description")
        fingerprint = alert.get("fingerprint", name)

        print(f"[ALERT] {status.upper()} | {name} | {region}/{hospital}")

        if status == "firing":
            # 1. Claude triage
            print(f"[AI] Asking Claude to triage {name}...")
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=300,
                messages=[{
                    "role": "user",
                    "content": f"""You are an SRE. Triage this alert in 3 bullet points max.

Alert: {name}
Severity: {severity}
Region: {region}
Hospital: {hospital}
Description: {description}"""
                }]
            )
            triage = response.content[0].text
            print(f"[AI TRIAGE]\n{triage}\n")

            # 2. ntfy
            requests.post(
                NTFY_URL,
                data=triage.encode("utf-8"),
                headers={
                    "Title": f"AI Triage: {name} ({region}/{hospital})",
                    "Priority": "high" if severity == "critical" else "default",
                    "Tags": "rotating_light,hospital"
                }
            )
            print(f"[NTFY] Sent")

            # 3. ServiceNow
            inc_number, sys_id = create_servicenow_incident(name, severity, region, hospital, triage)
            incident_map[fingerprint] = sys_id
            print(f"[SERVICENOW] Incident created: {inc_number} (sys_id={sys_id})")

        elif status == "resolved":
            sys_id = incident_map.pop(fingerprint, None)
            if sys_id:
                resolve_servicenow_incident(sys_id, name)
                requests.post(
                    NTFY_URL,
                    data=f"Alert '{name}' has cleared on {region}/{hospital}.".encode("utf-8"),
                    headers={
                        "Title": f"RESOLVED: {name} ({region}/{hospital})",
                        "Priority": "default",
                        "Tags": "white_check_mark,hospital"
                    }
                )
                print(f"[NTFY] Resolved notification sent")
            else:
                print(f"[SERVICENOW] No tracked incident for {fingerprint} - skipping resolve")

    return {"received": len(alerts)}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/incidents")
def list_incidents():
    return {"open_incidents": incident_map}

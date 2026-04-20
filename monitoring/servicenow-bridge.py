from fastapi import FastAPI, Request
import httpx
import json
import os

app = FastAPI()

SN_INSTANCE = "dev385935.service-now.com"
SN_USER     = "admin"
SN_PASSWORD = "GAl2g@cR4Tf-"
SN_TABLE    = "incident"
MAP_FILE    = "/home/ec2-user/incident_map.json"

def load_map():
    try:
        with open(MAP_FILE) as f:
            return json.load(f)
    except:
        return {}

def save_map(data):
    with open(MAP_FILE, "w") as f:
        json.dump(data, f)

@app.post("/webhook")
async def handle_alert(request: Request):
    payload = await request.json()
    incident_map = load_map()

    for alert in payload.get("alerts", []):
        status      = alert.get("status")
        labels      = alert.get("labels", {})
        annotations = alert.get("annotations", {})

        alertname   = labels.get("alertname")
        severity    = labels.get("severity", "warning")
        region      = labels.get("region", "unknown")
        hospital    = labels.get("hospital", "unknown")
        summary     = annotations.get("summary", alertname)
        description = annotations.get("description", "")
        runbook     = annotations.get("runbook", "No runbook linked")
        alert_key   = f"{alertname}-{region}"

        if status == "firing" and alert_key not in incident_map:
            severity_map = {"critical": "1", "warning": "2"}

            incident = {
                "short_description": f"[{region.upper()}] {summary}",
                "description": f"Alert: {alertname}\nRegion: {region}\nHospital: {hospital}\nSeverity: {severity}\n\nDescription: {description}\n\nRunbook: {runbook}",
                "severity":  severity_map.get(severity, "2"),
                "urgency":   severity_map.get(severity, "2"),
                "impact":    severity_map.get(severity, "2"),
                "category":  "Infrastructure",
                "assignment_group": "Service Desk",
                "work_notes": f"Auto-created by Hospital SRO monitoring.\nRegion: {region}\nHospital: {hospital}"
            }

            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"https://{SN_INSTANCE}/api/now/table/{SN_TABLE}",
                    json=incident,
                    auth=(SN_USER, SN_PASSWORD),
                    headers={"Content-Type": "application/json", "Accept": "application/json"}
                )
                if response.status_code == 201:
                    result = response.json().get("result", {})
                    incident_map[alert_key] = result.get("sys_id")
                    save_map(incident_map)
                    print(f"Created {result.get('number')} for {alert_key}")
                else:
                    print(f"Failed: {response.status_code} {response.text}")

        elif status == "resolved":
            sys_id = incident_map.get(alert_key)
            if sys_id:
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.patch(
                        f"https://{SN_INSTANCE}/api/now/table/{SN_TABLE}/{sys_id}",
                        json={
                            "state": "6",
                            "caller_id": "admin",
                            "close_code": "Solved (Permanently)",
                            "close_notes": f"Auto-resolved. Alert cleared in region: {region}"
                        },
                        auth=(SN_USER, SN_PASSWORD),
                        headers={"Content-Type": "application/json"}
                    )
                    if response.status_code == 200:
                        print(f"Resolved incident for {alert_key}")
                    del incident_map[alert_key]
                    save_map(incident_map)

    return {"status": "ok"}

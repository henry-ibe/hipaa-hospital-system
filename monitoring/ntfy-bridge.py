from fastapi import FastAPI, Request
import httpx
import asyncio

app = FastAPI()

NTFY_TOPIC = "https://ntfy.sh/henry-hospital-sro"

@app.post("/webhook")
async def handle_alert(request: Request):
    payload = await request.json()
    
    for alert in payload.get("alerts", []):
        status    = alert.get("status")
        alertname = alert["labels"].get("alertname")
        region    = alert["labels"].get("region", "unknown")
        hospital  = alert["labels"].get("hospital", "unknown")
        severity  = alert["labels"].get("severity", "warning")
        summary   = alert["annotations"].get("summary", alertname)

        if status == "firing":
            title    = f"FIRING: {alertname}"
            message  = f"{summary} | Region: {region} | Hospital: {hospital}"
            priority = "urgent" if severity == "critical" else "default"
            tags     = "rotating_light,hospital"
        else:
            title    = f"RESOLVED: {alertname}"
            message  = f"{summary} is now resolved in {region}"
            priority = "default"
            tags     = "white_check_mark,hospital"

        async with httpx.AsyncClient() as client:
            await client.post(
                NTFY_TOPIC,
                content=message,
                headers={
                    "Title": title,
                    "Priority": priority,
                    "Tags": tags
                }
            )
    
    return {"status": "ok"}

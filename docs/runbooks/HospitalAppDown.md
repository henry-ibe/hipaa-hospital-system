# Runbook: HospitalAppDown

## Summary
The hospital FastAPI application is unreachable. Prometheus `up` metric returned 0 for more than 10 seconds.

## Impact
- All hospital staff cannot access patient records
- Admissions, prescriptions, and billing are blocked
- Patient safety risk if clinical staff cannot access records

## Severity
Critical — P1

## Immediate Steps
1. Check if the process is running:
```bash
   sudo systemctl status hospital-app
```
2. If stopped, restart it:
```bash
   sudo systemctl start hospital-app
```
3. Check application logs:
```bash
   sudo journalctl -u hospital-app --no-pager | tail -50
```
4. Verify it responds:
```bash
   curl http://localhost:8000/health
```

## Common Causes
- Out of memory — OOM killer terminated the process
- Disk full — app cannot write logs
- Dependency failure — database unreachable
- Bad deployment — new code introduced a startup error

## Escalation
If app does not restart within 5 minutes escalate to application team.

## Related Alerts
- HighMemory
- DiskSpaceLow
- DBConnectionPoolHigh

# Runbook: HighErrorRate

## Summary
More than 5% of API requests are returning 5xx errors over a 5-minute window.

## Impact
- Hospital staff receiving errors on critical workflows
- Patient data may not be saving correctly
- Billing and prescription endpoints may be failing

## Severity
Critical — P1

## Immediate Steps
1. Check which endpoints are failing:
```bash
   curl -s http://localhost:8000/metrics | grep hospital_api_requests_total
```
2. Check application logs for errors:
```bash
   sudo journalctl -u hospital-app --no-pager | grep ERROR | tail -30
```
3. Check database connectivity:
```bash
   curl http://localhost:8000/health
```
4. Check if a recent deployment caused this:
```bash
   git log --oneline -5
```

## Common Causes
- Database connection pool exhausted
- Bad deployment introducing bugs
- Downstream dependency failure
- Memory pressure causing timeouts

## Escalation
If error rate exceeds 20% for more than 2 minutes, escalate to application team immediately.

# Runbook: HighCPU

## Summary
CPU usage exceeded 85% for more than 5 minutes.

## Severity
Warning — P2

## Immediate Steps
1. Identify the process consuming CPU:
```bash
   top
   ps aux --sort=-%cpu | head -10
```
2. Check if traffic spike is causing it:
```bash
   curl -s http://localhost:8000/metrics | grep api_requests_total
```
3. Check for runaway processes

## Common Causes
- Traffic spike
- Runaway process or infinite loop
- Prometheus scraping too frequently

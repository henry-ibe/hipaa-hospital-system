# Runbook: HighMemory

## Summary
Memory usage exceeded 90%. OOM killer may terminate processes.

## Severity
Critical — P1

## Immediate Steps
1. Check memory usage:
```bash
   free -h
   ps aux --sort=-%mem | head -10
```
2. Identify memory-hungry process
3. Restart Grafana if it is the culprit:
```bash
   sudo systemctl restart grafana-server
```
4. Restart hospital app if needed:
```bash
   sudo systemctl restart hospital-app
```

## Common Causes
- Grafana loading large dashboards
- Memory leak in application
- Too many concurrent connections

# Runbook: DiskSpaceLow

## Summary
Less than 15% disk space remaining on root volume.

## Impact
- Application cannot write logs
- Prometheus cannot store metrics
- Database writes may fail

## Severity
Warning — P2

## Immediate Steps
1. Check disk usage:
```bash
   df -h
   du -sh /* 2>/dev/null | sort -rh | head -10
```
2. Clear old logs:
```bash
   sudo journalctl --vacuum-time=7d
```
3. Clear old Prometheus data if needed:
```bash
   sudo find /var/lib/prometheus -name "*.tmp" -delete
```

## Escalation
If disk hits 5% free — escalate immediately. App will crash when disk is full.

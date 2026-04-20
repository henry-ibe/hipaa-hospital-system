# Runbook: DBConnectionPoolHigh

## Summary
Database connection pool usage exceeded 85%. Pool exhaustion will cause cascading 5xx errors.

## Impact
- Imminent risk of total application failure
- All database operations will fail if pool hits 100%

## Severity
Critical — P1

## Immediate Steps
1. Check current pool usage:
```bash
   curl -s http://localhost:8000/metrics | grep db_connection_pool
```
2. Check for slow queries holding connections:
```bash
   sudo journalctl -u hospital-app | grep "slow\|timeout\|connection" | tail -20
```
3. Increase pool size if needed:
```bash
   sudo systemctl edit hospital-app
   # Add: Environment="DB_POOL_SIZE=25"
   sudo systemctl restart hospital-app
```
4. If pool is at 100% — restart app immediately to reset connections

## Common Causes
- Traffic spike
- Slow queries holding connections too long
- Connection leak in application code

# Runbook: HighLatency

## Summary
P99 API latency has exceeded 2 seconds for more than 5 minutes.

## Impact
- Hospital staff experiencing slow response times
- Clinical workflows delayed

## Severity
Warning — P2

## Immediate Steps
1. Check which endpoints are slow:
```bash
   curl -s http://localhost:8000/metrics | grep hospital_api_duration
```
2. Check CPU and memory:
```bash
   top
   free -h
```
3. Check DB connection pool:
```bash
   curl -s http://localhost:8000/metrics | grep db_connection_pool
```

## Common Causes
- Slow database queries
- High CPU from traffic spike
- Memory pressure causing GC pauses
- Connection pool near exhaustion

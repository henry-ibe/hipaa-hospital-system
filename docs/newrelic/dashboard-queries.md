# New Relic NRQL Dashboard Queries — Hospital SRO TX

## Availability SLO
```sql
SELECT percentage(count(*), WHERE error IS false) 
AS 'Availability %' 
FROM Transaction 
WHERE appName = 'Hospital Management System - TX' 
SINCE 1 hour ago
```

## P99 Latency
```sql
SELECT percentile(duration, 99) AS 'P99 (s)' 
FROM Transaction 
WHERE appName = 'Hospital Management System - TX' 
SINCE 30 minutes ago
```

## Throughput Over Time
```sql
SELECT rate(count(*), 1 minute) AS 'Requests/min' 
FROM Transaction 
WHERE appName = 'Hospital Management System - TX' 
TIMESERIES 1 minute 
SINCE 1 hour ago
```

## Top Slowest Endpoints
```sql
SELECT average(duration) AS 'Avg duration' 
FROM Transaction 
WHERE appName = 'Hospital Management System - TX' 
FACET name 
SINCE 1 hour ago 
LIMIT 10
```

## Error Rate by Endpoint
```sql
SELECT percentage(count(*), WHERE error IS true) 
FROM Transaction 
WHERE appName = 'Hospital Management System - TX' 
FACET name 
SINCE 1 hour ago
```

## CPU Usage
```sql
SELECT average(cpuPercent) 
FROM SystemSample 
WHERE displayName = 'hospital-app-tx' 
TIMESERIES 1 minute 
SINCE 1 hour ago
```

## Memory Usage
```sql
SELECT average(memoryUsedPercent) 
FROM SystemSample 
WHERE displayName = 'hospital-app-tx' 
TIMESERIES 1 minute 
SINCE 1 hour ago
```

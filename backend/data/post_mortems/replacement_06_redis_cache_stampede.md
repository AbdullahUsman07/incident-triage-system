# Post-Mortem: Redis Cache Stampede Overwhelming Primary Database
## Incident Summary
Main PostgreSQL instance CPU usage spiked to 100%, causing cascading timeouts across web endpoints.

## Root Cause
Popular cache key expired without lock protection, causing thousands of concurrent requests to hit the primary DB simultaneously (Thundering Herd Problem).

## Stack Trace Pattern
`redis.exceptions.ConnectionError: Connection closed by server; postgresql TimeoutError: Query read timeout after 10000ms`

## Resolution
1. Implemented probabilistic early expiration (XFetch algorithm) and mutex locking on cache rebuilds.
2. Increased Redis instance memory tier.
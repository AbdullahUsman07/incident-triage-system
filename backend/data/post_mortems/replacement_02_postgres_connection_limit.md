# Post-Mortem: PostgreSQL Database Max Connections Reached
## Incident Summary
API gateways returned HTTP 500 errors as backend workers failed to establish database connections.

## Root Cause
Unclosed database handles in async background tasks exhausted the PostgreSQL connection pool limit (max_connections = 100).

## Stack Trace Pattern
`sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) FATAL: remaining connection slots are reserved for non-replication superuser connections`

## Resolution
1. Deployed PgBouncer for transactional connection pooling.
2. Fixed connection leakage in async worker cleanup routines.
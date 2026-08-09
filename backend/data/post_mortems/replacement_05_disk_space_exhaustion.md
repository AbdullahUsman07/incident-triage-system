# Post-Mortem: Server Disk Space Exhaustion via Log Explosion
## Incident Summary
Database node ceased accepting write operations and worker threads crashed with IO errors.

## Root Cause
`logrotate` daemon failed to compress stdout log streams, allowing debug logs to consume 100% of the root partition (`/var/log`).

## Stack Trace Pattern
`OSError: [Errno 28] No space left on device: '/var/log/app/application.log'`

## Resolution
1. Cleared stale uncompressed logs and restarted logrotate service.
2. Provisioned dedicated persistent volumes for logging paths with retention limits.
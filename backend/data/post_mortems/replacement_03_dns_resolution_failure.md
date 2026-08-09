# Post-Mortem: Microservice DNS Failure via CoreDNS Outage
## Incident Summary
Internal service-to-service communication dropped completely across cluster nodes with `ENOTFOUND` errors.

## Root Cause
CoreDNS pods entered a crash loop due to a corrupted ConfigMap rollout, breaking internal `.cluster.local` domain resolution.

## Stack Trace Pattern
`FetchError: request to http://auth-service.internal failed, reason: getaddrinfo ENOTFOUND auth-service.internal`

## Resolution
1. Reverted CoreDNS ConfigMap to previous stable version.
2. Scaled CoreDNS replica set across multiple availability zones.
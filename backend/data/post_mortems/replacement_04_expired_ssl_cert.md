# Post-Mortem: API Gateway Outage via Expired TLS Certificate
## Incident Summary
All external client requests were rejected with SSL handshake verification errors.

## Root Cause
Automated Let's Encrypt cert-manager renewal failed silently due to a misconfigured HTTP-01 challenge ingress rule.

## Stack Trace Pattern
`requests.exceptions.SSLError: HTTPSConnectionPool(host='api.example.com', port=443): Max retries exceeded with url: /v1/data (Caused by SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate has expired')))`

## Resolution
1. Manually reissued wildcard TLS certificate.
2. Fixed ingress routing rule for ACME HTTP-01 challenges and added Prometheus cert expiry alerts.
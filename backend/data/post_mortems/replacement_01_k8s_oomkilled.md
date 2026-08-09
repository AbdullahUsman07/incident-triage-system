# Post-Mortem: Kubernetes Pod OOMKilled (Exit Code 137)
## Incident Summary
Worker pods running image-processing tasks crashed continuously with status `OOMKilled` and container exit code 137.

## Root Cause
Memory leak in buffer processing accumulated uncollected byte arrays in RAM. Pod cgroup limits (512MB) were exceeded, triggering Linux kernel OOM killer.

## Stack Trace Pattern
`Container worker-pod-a7f terminated with exit code 137 (OOMKilled)`

## Resolution
1. Increased pod memory limits from 512MB to 2GB in deployment manifests.
2. Refactored image processor to stream chunks rather than loading full files into memory.
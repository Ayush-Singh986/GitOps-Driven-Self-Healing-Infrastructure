# Runbook: OOMKilled (Out Of Memory)
## Diagnosis
- **Symptom:** Pod status is `OOMKilled`.
- **Metrics to check:** `container_memory_working_set_bytes` vs `kube_pod_container_resource_limits`.
- **Log Pattern:** "Out of memory: Kill process".

## Remediation
- **Safe Fix:** Increase memory limits in the deployment manifest by 20-50%.
- **Risky Fix:** Reducing other pods' resources to make room.
- **Escalation:** If memory usage grows linearly regardless of limits (Memory Leak), escalate to Engineering.

---
# Runbook: CrashLoopBackOff
## Diagnosis
- **Symptom:** Pod keeps restarting.
- **Logs to check:** Search for `Panic`, `Error`, or `Exception` in the last 100 lines of logs.
- **Events:** `kubectl describe pod` showing failing liveness/readiness probes.

## Remediation
- **Safe Fix:** If caused by a temporary dependency failure, restart the deployment.
- **Risky Fix:** Changing environment variables or image versions.
- **Escalation:** Code-level crash or configuration error requires human intervention.

---
# Runbook: Disk Pressure
## Diagnosis
- **Symptom:** `DiskPressure` condition on node.
- **Metrics:** `node_filesystem_avail_bytes`.

## Remediation
- **Safe Fix:** Clear ephemeral caches or increase PVC size via GitOps.
- **Risky Fix:** Deleting old PVCs or logs.
- **Escalation:** Persistent storage full across the cluster.

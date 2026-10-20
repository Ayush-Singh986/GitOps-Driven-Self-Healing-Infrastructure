from kubernetes import client, config
import datetime

class K8sTools:
    def __init__(self):
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config()
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()

    def get_incident_context(self, alert_id: str) -> str:
        # In a real scenario, alert_id maps to a specific pod/namespace
        # For the demo, we'll look for pods in 'CrashLoopBackOff' or 'OOMKilled'
        context = []
        pods = self.v1.list_pod_for_all_namespaces(watch=False)
        for pod in pods.items:
            for status in (pod.status.container_statuses or []):
                if status.state.waiting and status.state.waiting.reason in ["CrashLoopBackOff", "OOMKilled"]:
                    context.append(f"Pod: {pod.metadata.name}, Reason: {status.state.waiting.reason}")
                    logs = self.v1.read_namespaced_pod_log(pod.metadata.name, pod.metadata.namespace, tail=50)
                    context.append(f"Logs: {logs}")

        return "\n".join(context) if context else "No failing pods found."

    def apply_fix(self, fix_description: str) -> str:
        # Mock implementation for demo purposes
        # Real implementation would use GitOps: update YAML in Git -> ArgoCD Sync
        return f"Successfully triggered GitOps PR for: {fix_description}"

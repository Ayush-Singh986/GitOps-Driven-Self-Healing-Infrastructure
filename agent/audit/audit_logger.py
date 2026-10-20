import datetime
import json

class AuditLogger:
    def __init__(self, log_file="agent_audit.log"):
        self.log_file = log_file

    def log_action(self, alert_id, state):
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "alert_id": alert_id,
            "incident_type": state.get("incident_type"),
            "decision": state.get("decision"),
            "action": state.get("action_taken"),
            "context": state.get("context")
        }
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

import chromadb
from chromadb.utils import embedding_functions

class RunbookEngine:
    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(name="runbooks")
        self._seed_runbooks()

    def _seed_runbooks(self):
        # In reality, this reads from runbooks/standard_runbooks.md
        runbooks = [
            {"id": "oom", "text": "For OOMKilled, increase memory limits in deployment manifest by 20%."},
            {"id": "crash", "text": "For CrashLoopBackOff, check logs for panic; if transient, restart deployment."},
            {"id": "disk", "text": "For DiskPressure, clear temporary caches or increase PVC size."}
        ]
        self.collection.add(
            documents=[rb["text"] for rb in runbooks],
            ids=[rb["id"] for rb in runbooks]
        )

    def query_runbook(self, context: str) -> str:
        results = self.collection.query(
            query_texts=[context],
            n_results=1
        )
        return results['documents'][0][0] if results['documents'] else "No runbook found."

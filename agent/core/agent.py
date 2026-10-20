import os
from typing import TypedDict, List, Optional
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from agent.tools.k8s_tools import K8sTools
from agent.rag.runbook_engine import RunbookEngine

# Define the state of the agent
class AgentState(TypedDict):
    alert_id: str
    incident_type: Optional[str]
    context: Optional[str]
    suggested_fix: Optional[str]
    decision: Optional[str] # 'safe' or 'risky'
    action_taken: Optional[str]
    error: Optional[str]

class RemediationAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4-turbo-preview")
        self.k8s = K8sTools()
        self.rag = RunbookEngine()

        # Initialize the LangGraph
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("diagnose", self.diagnose_incident)
        workflow.add_node("retrieve_fix", self.retrieve_fix)
        workflow.add_node("decide_action", self.decide_action)
        workflow.add_node("execute_remediation", self.execute_remediation)

        # Define edges
        workflow.set_entry_point("diagnose")
        workflow.add_edge("diagnose", "retrieve_fix")
        workflow.add_edge("retrieve_fix", "decide_action")

        # Conditional edge: safe -> execute, risky -> end (escalate)
        workflow.add_conditional_edges(
            "decide_action",
            self.should_execute,
            {
                "execute": "execute_remediation",
                "escalate": END
            }
        )
        workflow.add_edge("execute_remediation", END)

        self.app = workflow.compile()

    def diagnose_incident(self, state: AgentState):
        print(f"🔍 Diagnosing incident: {state['alert_id']}")
        # Tool use: Get logs and events
        context = self.k8s.get_incident_context(state['alert_id'])
        return {"context": context}

    def retrieve_fix(self, state: AgentState):
        print("📚 Retrieving fix from Runbook RAG...")
        fix = self.rag.query_runbook(state['context'])
        return {"suggested_fix": fix}

    def decide_action(self, state: AgentState):
        print("⚖️ Deciding if fix is safe or risky...")
        prompt = f"Based on this fix: {state['suggested_fix']}, is this 'safe' (e.g. restart, scale) or 'risky' (e.g. delete PVC, change image)? Answer only 'safe' or 'risky'."
        decision = self.llm.invoke(prompt).content.strip().lower()
        return {"decision": decision}

    def should_execute(self, state: AgentState):
        if state['decision'] == 'safe':
            return "execute"
        return "escalate"

    def execute_remediation(self, state: AgentState):
        print(f"🚀 Executing safe remediation: {state['suggested_fix']}")
        result = self.k8s.apply_fix(state['suggested_fix'])
        return {"action_taken": result}

    def run(self, alert_id: str):
        inputs = {"alert_id": alert_id}
        return self.app.invoke(inputs)

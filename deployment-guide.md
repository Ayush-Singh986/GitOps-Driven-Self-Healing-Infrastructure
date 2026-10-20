# 📘 Deep-Dive Deployment Guide

This document provides the technical specifications for deploying OmniRoute in a production-like environment.

## 🛠️ Component Architecture

### 1. The Control Plane (FastAPI)
The backend is designed as a stateless API. In a production environment, it should be deployed as a Kubernetes Deployment with a Horizontal Pod Autoscaler (HPA).
- **Port:** 8000
- **Health Check:** `/health`
- **Resources:** Recommended 512Mi RAM, 250m CPU.

### 2. The AI Agent (LangGraph)
The agent uses a stateful graph. The state is currently kept in memory. For a production multi-user environment, the `AgentState` should be backed by a **Redis** or **PostgreSQL** checkpointer.

### 3. The Knowledge Base (ChromaDB)
The runbooks are embedded into a vector space. To ensure persistence across pod restarts, the ChromaDB storage should be mounted to a **PersistentVolumeClaim (PVC)** using an AWS EBS or GCP Persistent Disk.

### 4. The GitOps Loop (ArgoCD)
The agent is configured to commit changes to a specific branch (e.g., `remediation-branch`). 
- **ArgoCD Sync Policy:** Set to `Manual` or `Automated with Prune`.
- **Validation:** It is recommended to add a GitHub Action that runs `kube-linter` or `datree` on the agent's PR before it is merged.

## 🚀 Production Deployment Checklist

- [ ] **Secrets Management:** Move `OPENAI_API_KEY` from environment variables to **Kubernetes Secrets** or **HashiCorp Vault**.
- [ ] **Ingress:** Set up an Nginx Ingress Controller to expose the Dashboard via HTTPS.
- [ ] **Monitoring:** Add a Prometheus rule to monitor the `agent_audit.log` for high failure rates.
- [ ] **Backup:** Implement a backup strategy for the ChromaDB vector store.

## 🛡️ Security Audit
- **RBAC:** The `ai-remediation-role` follows the principle of least privilege. It cannot delete namespaces or modify cluster-level security policies.
- **Validation:** The Human-in-the-Loop (HITL) gate prevents the AI from executing destructive commands without oversight.

# GitOps-Driven Self-Healing Infrastructure
An autonomous AI agent for incident detection & remediation (AIOps).

## 🏗️ Architecture
This project implements an AIOps loop:
`Alertmanager` $\rightarrow$ `LangGraph Agent` $\rightarrow$ `Prometheus/Loki` (Context) $\rightarrow$ `Runbooks` (RAG) $\rightarrow$ `ArgoCD` (Remediation).

## 🛠️ Tech Stack
- **Agent Framework:** LangGraph, Kubernetes Python Client
- **Observability:** Prometheus, Loki, Alertmanager
- **GitOps:** ArgoCD
- **Guardrails:** K8s RBAC, Audit Logging
- **Infrastructure:** Kubernetes (Kind/Minikube)

## 🚀 Getting Started
(Detailed setup guide to be added)

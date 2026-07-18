  # 🛡️ ShadowDeploy - AI-Powered Kubernetes Incident Response Platform
 
ShadowDeploy is an AI-powered Kubernetes incident response platform that automatically detects pod failures, collects logs, performs root cause analysis using a locally running Large Language Model (Ollama), stores incidents in SQLite through FastAPI, sends email alerts, and visualizes operational metrics using Prometheus and Grafana.
 
Unlike cloud-based AI solutions, ShadowDeploy runs completely locally, ensuring privacy, low cost, and no external API dependency.
 
---
 
# ✨ Features
 
- Detects Kubernetes pod failures automatically
- Collects pod logs
- AI-powered Root Cause Analysis using Ollama
- Stores incidents in SQLite
- FastAPI REST API
- HTML Email Alerts
- Prometheus Metrics
- Grafana Dashboard
- Completely Local (No OpenAI API required)
 
---
 
# 🏗️ Architecture
 
```text
Kubernetes
     │
     ▼
ShadowDeploy Watcher
     │
     ▼
Log Collector
     │
     ▼
Ollama (Local LLM)
     │
     ▼
FastAPI API
     │
     ▼
SQLite Database
     │
     ├────────► Email Alerts
     │
     ▼
Prometheus
     │
     ▼
Grafana Dashboard
```
 
---
 
# ⚙️ Tech Stack
 
| Component | Technology |
|-----------|------------|
| Language | Python 3.11 |
| Container Orchestration | Kubernetes (Minikube) |
| API | FastAPI |
| AI | Ollama (Mistral / Llama3) |
| Database | SQLite |
| Monitoring | Prometheus |
| Visualization | Grafana |
| Alerts | Gmail SMTP |
| Container Runtime | Docker |
| Package Manager | Helm |
 
---
 
# 🚨 Failure Types Supported
 
- CrashLoopBackOff
- ImagePullBackOff
- ErrImagePull
- OOMKilled
- FailedScheduling
- Failed Health Checks
- Missing Environment Variables
 
---
 
# 📁 Project Structure
 
```text
shadowdeploy
│
├── agent
│   ├── watcher.py
│   ├── log_collector.py
│   ├── ai_analyzer.py
│   ├── alert_sender.py
│   └── metrics.py
│
├── api
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── routes
│
├── apps
├── database
├── docker
├── k8s
├── monitoring
├── requirements.txt
├── config.py
└── README.md
```
 
---
 
# 📋 Prerequisites
 
- Python 3.11+
- Docker Desktop
- Minikube
- kubectl
- Helm
- Ollama
 
---
 
# 🚀 Installation
 
### Clone the repository
 
```bash
git clone https://github.com/YOUR_USERNAME/shadowdeploy.git
 
cd shadowdeploy
```
 
### Create a virtual environment
 
```bash
python -m venv venv
```
 
### Activate the virtual environment
 
**Windows**
 
```powershell
venv\Scripts\activate
```
 
**Linux/macOS**
 
```bash
source venv/bin/activate
```
 
### Install dependencies
 
```bash
pip install -r requirements.txt
```
 
### Copy the environment file
 
**Windows**
 
```powershell
copy .env.example .env
```
 
### Install the Ollama model
 
```bash
ollama pull mistral
```
 
### Start Minikube
 
```bash
minikube start
```
 
### Deploy the sample applications
 
```powershell
minikube docker-env --shell powershell | Invoke-Expression
 
docker build -t bad-port-app:latest ./apps/bad-port
 
docker build -t crashloop-app:latest ./apps/crashloop
 
docker build -t missing-env-app:latest ./apps/missing-env
 
docker build -t oom-kill-app:latest ./apps/oom-kill
 
docker build -t bad-image-app:latest ./apps/bad-image
 
kubectl apply -f k8s/failing-apps/
```
 
---
 
# ▶️ Running the Project
 
### Terminal 1
 
```bash
ollama serve
```
 
### Terminal 2
 
```bash
uvicorn api.main:app --reload --port 8000
```
 
### Terminal 3
 
```bash
python -m agent.watcher
```
 
---
 
# 🌐 API
 
### Swagger UI
 
```
http://localhost:8000/docs
```
 
### Metrics
 
```
http://localhost:8000/metrics
```
 
### Statistics
 
```
http://localhost:8000/api/stats
```
 
---
 
# 📊 Monitoring
 
### Prometheus
 
```bash
minikube service monitoring-kube-prometheus-prometheus
```
 
### Grafana
 
```bash
minikube service monitoring-grafana
```
 
---
 
# 🚀 Future Enhancements
 
- Telegram Notifications
- Slack Integration
- Microsoft Teams Alerts
- Incident Auto-remediation
- Multi-cluster Monitoring
- PostgreSQL Support
- Kubernetes Operator
- AI-generated RCA Reports (PDF)
- Role-based Authentication
- React Dashboard
 
---
 
# 👨‍💻 Built By
 
**Sanskruti Nainesh Chavan**
 
**Pranav Chaudhari**

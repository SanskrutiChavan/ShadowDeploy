**ShadowDeploy - AI-Powered Kubernetes Incident Response Platform**



ShadowDeploy is an AI-powered Kubernetes incident response platform that automatically detects pod failures, collects logs, performs root cause analysis using a locally running Large Language Model (Ollama), stores incidents in SQLite through FastAPI, sends email alerts, and visualizes operational metrics using Prometheus and Grafana.



Unlike cloud-based AI solutions, ShadowDeploy runs completely locally, ensuring privacy, low cost, and no external API dependency.



\--------------------------------------------------------------------------------------------------------------

**Features**



\- Detects Kubernetes pod failures automatically

\- Collects pod logs

\- AI-powered Root Cause Analysis using Ollama

\- Stores incidents in SQLite

\- FastAPI REST API

\- HTML Email Alerts

\- Prometheus Metrics

\- Grafana Dashboard

\- Completely Local (No OpenAI API required)



\--------------------------------------------------------------------------------------------------------------

**Architecture**



Kubernetes

&#x20;    │

&#x20;    ▼

ShadowDeploy Watcher

&#x20;    │

&#x20;    ▼

Log Collector

&#x20;    │

&#x20;    ▼

Ollama (Local LLM)

&#x20;    │

&#x20;    ▼

FastAPI API

&#x20;    │

&#x20;    ▼

SQLite Database

&#x20;    │

&#x20;    ├────────► Email Alerts

&#x20;    │

&#x20;    ▼

Prometheus

&#x20;    │

&#x20;    ▼

Grafana Dashboard



\--------------------------------------------------------------------------------------------------------------

**Tech Stack**



Component  				Technology

&#x09;

Language  				Python 3.11

Container Orchestration 		Kubernetes (Minikube)

API 					FastAPI

AI 					Ollama (Mistral / Llama3)

Database 				SQLite

Monitoring  				Prometheus

Visualization 				Grafana

Alerts 					Gmail SMTP

Container Runtime 			Docker

Package Manager  			Helm



\--------------------------------------------------------------------------------------------------------------

**Failure Types Supported**



\- CrashLoopBackOff

\- ImagePullBackOff

\- ErrImagePull

\- OOMKilled

\- FailedScheduling

\- Failed Health Checks

\- Missing Environment Variables



\--------------------------------------------------------------------------------------------------------------

**Project Structure**



shadowdeploy

│

├── agent

│   ├── watcher.py

│   ├── log\_collector.py

│   ├── ai\_analyzer.py

│   ├── alert\_sender.py

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

\--------------------------------------------------------------------------------------------------------------

**Prerequisites**



\- Python 3.11+

\- Docker Desktop

\- Minikube

\- kubectl

\- Helm

\- Ollama



\--------------------------------------------------------------------------------------------------------------

**Installation**



Clone the repository

git clone https://github.com/YOUR\_USERNAME/shadowdeploy.git

cd shadowdeploy





Create virtual environment
python -m venv venv




Activate Windows
venv\\Scripts\\activate




Linux/macOS

source venv/bin/activate



Install dependencies
pip install -r requirements.txt




Copy environment file
copy .env.example .env




Install Ollama model
ollama pull mistral


Start Minikube
minikube start


Deploy the sample applications
minikube docker-env --shell powershell | Invoke-Expression

docker build -t bad-port-app:latest ./apps/bad-port

docker build -t crashloop-app:latest ./apps/crashloop

docker build -t missing-env-app:latest ./apps/missing-env

docker build -t oom-kill-app:latest ./apps/oom-kill

docker build -t bad-image-app:latest ./apps/bad-image

kubectl apply -f k8s/failing-apps/


\--------------------------------------------------------------------------------------------------------------

Running the Project



Terminal 1
ollama serve



Terminal 2
uvicorn api.main:app --reload --port 8000


Terminal 3
python -m agent.watcher

\--------------------------------------------------------------------------------------------------------------

API



Swagger UI

http://localhost:8000/docs


Metrics
http://localhost:8000/metrics


Statistics
http://localhost:8000/api/stats
--------------------------------------------------------------------------------------------------------------

Monitoring



Prometheus
minikube service monitoring-kube-prometheus-prometheus


Grafana
minikube service monitoring-grafana
--------------------------------------------------------------------------------------------------------------

Future Enhancements



\- Telegram Notifications

\- Slack Integration

\- Microsoft Teams Alerts

\- Incident Auto-remediation

\- Multi-cluster Monitoring

\- PostgreSQL Support

\- Kubernetes Operator

\- AI-generated RCA Reports (PDF)

\- Role-based Authentication

\- React Dashboard



\--------------------------------------------------------------------------------------------------------------

Built by Sanskruti Nainesh Chavan and Pranav Chaudhari


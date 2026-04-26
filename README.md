# 🏥 HIPAA-Compliant Hospital Management System — SRE Observability Platform

> A production-grade cloud infrastructure project demonstrating multi-region AWS deployment, Infrastructure as Code, full SRE observability stack, AI-powered incident triage, automated incident management, and HIPAA-aligned security practices.

[![Terraform](https://img.shields.io/badge/IaC-Terraform-7B42BC?logo=terraform)](https://www.terraform.io/)
[![AWS](https://img.shields.io/badge/Cloud-AWS-FF9900?logo=amazonaws)](https://aws.amazon.com/)
[![Python](https://img.shields.io/badge/Backend-Python%20FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Prometheus](https://img.shields.io/badge/Metrics-Prometheus-E6522C?logo=prometheus)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Dashboards-Grafana-F46800?logo=grafana)](https://grafana.com/)
[![New Relic](https://img.shields.io/badge/APM-New%20Relic-008C99?logo=newrelic)](https://newrelic.com/)
[![ServiceNow](https://img.shields.io/badge/ITSM-ServiceNow-62D84E?logo=servicenow)](https://servicenow.com/)
[![Claude AI](https://img.shields.io/badge/AI-Claude%20by%20Anthropic-D97757?logo=anthropic)](https://anthropic.com/)
[![Live Demo](https://img.shields.io/badge/Live%20Portal-GitHub%20Pages-181717?logo=github)](https://henry-ibe.github.io/hipaa-hospital-system/)

---

## 📌 What Is This Project?

This project simulates a **real-world hospital IT infrastructure** running across multiple AWS regions. Originally built as a multi-region deployment platform, it has been extended into a **full SRE observability stack** — the kind of system a Site Reliability Engineer would design and operate for a regulated organization.

**The observability layer includes:**
- Prometheus metrics with labeled business data
- 8 Prometheus alert rules with full runbook coverage
- Alertmanager routing to Slack, phone notifications, and ServiceNow simultaneously
- Dynamic Grafana dashboards that auto-configure when a new region deploys
- New Relic APM and infrastructure monitoring
- ServiceNow auto-incident creation and auto-resolution
- **AI-powered triage agent (Claude) — pre-investigates every alert before creating tickets**

---

## 🗺️ Full Architecture
┌─────────────────────────────────────────────────────────┐
│                  GitHub Pages Portal                    │
│            (Self-Service Deployment UI)                 │
└──────────────────────┬──────────────────────────────────┘
│ triggers
┌──────────────────────▼──────────────────────────────────┐
│                GitHub Actions CI/CD                     │
│           (Automated Terraform Pipelines)               │
└──────┬───────────────┬─────────────────────────────────┘
│               │
┌──────▼──┐       ┌────▼──────┐
│  AWS NY │       │   AWS CA  │
│ (Urban) │       │(Research) │
└──────┬──┘       └─────┬─────┘
└────────┬────────┘
│
┌───────────────▼──────────────────┐
│         Prometheus               │
│  (Metrics + 8 Alert Rules)       │
└───────────────┬──────────────────┘
│
┌───────────────▼──────────────────┐
│          Alertmanager            │
│    (Routing + Inhibition)        │
└──────┬──────────┬────────────────┘
│          │
│   ┌──────▼─────────────────────────┐
│   │      AI Triage Agent           │
│   │   (Claude by Anthropic)        │
│   │                                │
│   │  1. Receives alert webhook     │
│   │  2. Calls Claude API           │
│   │  3. Generates SRE triage       │
│   │  4. Enriches ServiceNow ticket │
│   │  5. Pushes smart ntfy alert    │
│   │  6. Auto-resolves on clear     │
│   └──────┬─────────────────────────┘
│          │
┌──────▼──┐  ┌────▼──────┐  ┌──────────────┐
│  Slack  │  │   ntfy    │  │  ServiceNow  │
│ #alerts │  │  (phone)  │  │ (AI-enriched)│
└─────────┘  └───────────┘  └──────────────┘
┌───────────────────────────────────┐
│            New Relic              │
│   APM + Infrastructure Agent      │
└───────────────────────────────────┘
┌───────────────────────────────────┐
│             Grafana               │
│  Dynamic dashboards (auto-config) │
└───────────────────────────────────┘

---

## 🤖 AI Triage Agent

**The most differentiated component of this project.**

Most SRE portfolios show Prometheus + Grafana. This project goes further — when an alert fires, an AI agent intercepts it, reasons about the root cause, and enriches the incident before a human ever sees it.

### How It Works
Alert fires in Prometheus
↓
Alertmanager webhook → AI Triage Agent (port 9000)
↓
Claude API analyzes: alert name, severity, region, hospital, description
↓
Generates structured SRE triage:
• Root cause hypothesis
• Immediate actions (3 bullet points)
• Remediation path
↓
┌─────────────────────────────────────────────┐
│  ntfy.sh  →  Smart push notification        │
│             "AI Triage: DiskSpaceLow —      │
│              check /var/log, implement      │
│              log rotation"                  │
└─────────────────────────────────────────────┘
↓
┌─────────────────────────────────────────────┐
│  ServiceNow  →  Enriched P1/P2 incident     │
│  Description contains full AI analysis,     │
│  not just "alert fired"                     │
└─────────────────────────────────────────────┘
↓
Alert resolves → ServiceNow auto-closed
→ Resolved ntfy notification sent

### Sample AI Triage Output
Alert: DiskSpaceLow | Region: NY | Hospital: NewYork

Immediate Action Required: SSH into NY hospital server and identify
largest consumers using du -sh /* and df -h. Critical severity
means potential service disruption imminent.
Root Cause: Likely culprits are logs, temp files, or database growth.
Check /var/log, /tmp, and application directories for oversized files
that can be safely archived or rotated.
Remediation Path:

Quick fix: Clear old logs/temp files to drop below 75%
Follow-up: Implement log rotation, increase disk capacity,
or add monitoring alert at 70% threshold




### Files
monitoring/ai-triage-agent/
├── agent.py          # FastAPI service — webhook receiver + Claude integration
├── requirements.txt  # fastapi, uvicorn, anthropic, requests, python-dotenv
└── .gitignore        # excludes venv/, .env, pycache

### Deploy
```bash
cd monitoring/ai-triage-agent
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Set env vars
export ANTHROPIC_API_KEY=sk-ant-...
export SN_INSTANCE=devXXXXX.service-now.com
export SN_USER=admin
export SN_PASSWORD=...

uvicorn agent:app --host 0.0.0.0 --port 9000
```

---

## 🏗️ Key Components

### 1. Infrastructure as Code (`main.tf`, `variables.tf`)
Full Terraform configuration for multi-region AWS deployment. Each region deploys EC2, VPC, subnets, security groups, ALB, WAF, and CloudFront.

### 2. FastAPI Backend (`app/main.py`)
Python REST API with JWT authentication, TOTP-based MFA, RBAC, and full Prometheus instrumentation. Exposes `/health` and `/metrics` endpoints for the monitoring stack.

### 3. Observability Stack (`monitoring/`)
Complete SRE monitoring pipeline:
- **Prometheus** — scrapes labeled metrics every 15 seconds
- **8 Alert Rules** — availability, latency, capacity, security, infrastructure
- **Alertmanager** — routes to Slack + ntfy + AI Triage Agent simultaneously
- **Grafana** — dynamic dashboards provisioned from code
- **New Relic** — APM traces, endpoint breakdown, NRQL dashboards

### 4. Incident Management Pipeline
Alert fires → Alertmanager routes simultaneously to:
├── Slack #sro-alerts       (team visibility)
├── AI Triage Agent         (Claude analysis + enrichment)
│   ├── ntfy phone push     (smart AI-generated summary)
│   └── ServiceNow ticket   (AI-enriched description)
Alert resolves → ServiceNow auto-closes, resolved ntfy sent

### 5. Runbooks (`docs/runbooks/`)
One runbook per alert rule. Each includes impact assessment, immediate steps with copy-pasteable commands, common causes, and escalation path. Linked directly from alert annotations and ServiceNow ticket descriptions.

### 6. Self-Service Deployment Portal (`deployment-portal/`)
Web UI on GitHub Pages for one-click region deployment via AWS Lambda backend.

### 7. CI/CD Pipeline (`.github/workflows/`)
GitHub Actions automates infrastructure validation and deployment.

---

## 🌍 Region Profiles

| Region | Hospital Model | Focus | Pricing |
|---|---|---|---|
| 🗽 New York | Urban High-Volume (Mount Sinai) | Emergency, Trauma | +30% NYC premium |
| 🌴 California | Research Hospital (UCLA) | Surgery, Radiology | Standard |
| 🤠 Texas | Urban Hospital (Presbyterian) | Emergency, General | Standard |

---

## 📊 Prometheus Alert Rules

| Alert | Condition | Severity |
|---|---|---|
| `HospitalAppDown` | App unreachable for 10s | Critical |
| `HighErrorRate` | 5xx rate >5% for 2min | Critical |
| `BedOccupancyCritical` | Department >95% capacity | Warning |
| `DBConnectionPoolHigh` | Pool usage >85% | Critical |
| `AuthFailureSpike` | Failed logins >0.5/sec | Warning |
| `HighCPU` | CPU >85% for 5min | Warning |
| `DiskSpaceLow` | Disk <15% free | Warning |
| `HighMemory` | Memory >90% for 5min | Critical |

Every alert links to a runbook in `docs/runbooks/`.

---

## 📈 Business Metrics Tracked

| Metric | Description |
|---|---|
| `hospital_patients_active` | Active patients by department and region |
| `hospital_bed_occupancy_ratio` | Bed occupancy % by department |
| `hospital_api_requests_total` | API requests by endpoint, status, region |
| `hospital_api_duration_seconds` | Request latency histogram |
| `hospital_billing_transactions_total` | Billing transactions by status |
| `hospital_billing_amount_dollars_total` | Revenue counter |
| `hospital_prescriptions_written_total` | Prescriptions by medication type |
| `hospital_auth_attempts_total` | Auth attempts by success/failure |
| `hospital_mfa_failures_total` | MFA failure counter |
| `hospital_db_connection_pool_usage` | DB pool utilization ratio |

---

## 🛡️ Security Features

- **JWT Authentication** — stateless token-based API access
- **TOTP / MFA** — time-based one-time password support
- **Rate Limiting** — API abuse prevention
- **AuthFailureSpike Alert** — brute force detection with automatic Slack notification
- **HIPAA-Aligned Design** — access controls, audit logging, data handling patterns

---

## 🛠️ Full Tech Stack

| Category | Technology |
|---|---|
| Cloud | AWS (EC2, VPC, Lambda, IAM, SSM, CloudFront, WAF) |
| IaC | Terraform (multi-region workspaces) |
| Backend | Python 3.12, FastAPI, SQLite |
| Metrics | Prometheus, Node Exporter |
| Alerting | Alertmanager, ntfy.sh bridge |
| Dashboards | Grafana (provisioned), New Relic (NRQL) |
| APM | New Relic Python agent + infrastructure agent |
| AI Triage | Claude by Anthropic (claude-haiku via API) |
| Incident Management | ServiceNow REST API (auto create/resolve) |
| Notifications | Slack incoming webhooks, ntfy.sh |
| OS | RHEL 9 on AWS |
| Process Management | systemd |
| Auth | JWT, TOTP |
| CI/CD | GitHub Actions |
| Frontend | HTML/CSS/JavaScript (GitHub Pages) |

---

## 🚀 Deployment

### Option 1: Self-Service Portal
Visit: **[henry-ibe.github.io/hipaa-hospital-system](https://henry-ibe.github.io/hipaa-hospital-system/)**

### Option 2: Terraform CLI

```bash
git clone https://github.com/henry-ibe/hipaa-hospital-system.git
cd hipaa-hospital-system

terraform init
terraform workspace new ny-hospital
terraform apply -var-file="ny-hospital.tfvars"
```

### Option 3: Manual EC2 Setup

```bash
pip3 install -r requirements.txt

export HOSPITAL_REGION=ny
export HOSPITAL_NAME=newyork
export SECRET_KEY=your-secret-key

uvicorn app.main:app --host 0.0.0.0 --port 8000

sudo cp monitoring/prometheus/prometheus.yml /etc/prometheus/
sudo cp monitoring/prometheus/rules/hospital-alerts.yml /etc/prometheus/rules/
sudo cp monitoring/alertmanager/alertmanager.yml /etc/alertmanager/
sudo systemctl restart prometheus alertmanager grafana-server

# Start AI triage agent
cd monitoring/ai-triage-agent
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn agent:app --host 0.0.0.0 --port 9000
```

---

## 📁 Repository Structure
hipaa-hospital-system/
├── .github/workflows/          # CI/CD pipeline
├── app/
│   └── main.py                 # FastAPI app + Prometheus instrumentation
├── docs/
│   ├── runbooks/               # One runbook per alert rule (8 total)
│   └── newrelic/
│       └── dashboard-queries.md
├── monitoring/
│   ├── ai-triage-agent/
│   │   ├── agent.py            # Claude AI triage agent (FastAPI)
│   │   └── requirements.txt
│   ├── alertmanager/
│   │   └── alertmanager.yml    # Routing: Slack + ntfy + AI agent
│   ├── grafana/
│   │   ├── dashboards/
│   │   └── provisioning/
│   ├── prometheus/
│   │   ├── prometheus.yml
│   │   └── rules/
│   │       └── hospital-alerts.yml
│   ├── ntfy-bridge.py
│   ├── servicenow-bridge.py
│   └── traffic-simulator.py
├── deployment-portal/
├── lambda-deployment-api/
├── main.tf
├── variables.tf
├── *-hospital.tfvars
└── WHITEPAPER.md

---

## 💡 SRE Concepts Demonstrated

| Concept | Implementation |
|---|---|
| Observability pillars | Metrics (Prometheus), APM traces (New Relic), logs (Grafana) |
| AI-assisted ops | Claude pre-triages every alert before human review |
| SLO-based alerting | Alerts tied to business impact not just infra health |
| Alert quality | Inhibition rules, repeat_interval tuning, signal-to-noise |
| Runbook-driven ops | Every alert links to actionable documentation |
| Dynamic provisioning | Grafana auto-configures from code, not manual clicks |
| Multi-destination routing | One alert fans out to phone, Slack, ITSM, and AI agent |
| Auto-remediation | Incidents auto-close when alerts resolve |
| IaC observability | Monitoring stack defined as code, reproducible |
| ITSM integration | ServiceNow REST API with SLA timers |
| Financial services patterns | Compliance-ready audit trail on every incident |

---

## 📄 Architecture Whitepaper

For a deep-dive into design decisions and infrastructure patterns see [`WHITEPAPER.md`](./WHITEPAPER.md).

---

## 👤 Author

**Henry Ibe** — Systems & Infrastructure Engineer
AWS Solutions Architect Associate | CKA | RHCSA | Terraform Associate | ServiceNow CSA | Linux+

[![GitHub](https://img.shields.io/badge/GitHub-henry--ibe-181717?logo=github)](https://github.com/henry-ibe)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-henry--ibe-0077B5?logo=linkedin)](https://linkedin.com/in/henry-ibe)

---

*This is a portfolio/lab project. No real patient data is used or stored.*

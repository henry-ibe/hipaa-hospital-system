# 🏥 HIPAA-Compliant Multi-Region Hospital Management System

> A production-grade cloud infrastructure project demonstrating multi-region AWS deployment, Infrastructure as Code, real-time monitoring, and HIPAA-aligned security practices — built as a DevOps/Cloud Engineering portfolio piece.

[![Terraform](https://img.shields.io/badge/IaC-Terraform-7B42BC?logo=terraform)](https://www.terraform.io/)
[![AWS](https://img.shields.io/badge/Cloud-AWS-FF9900?logo=amazonaws)](https://aws.amazon.com/)
[![Python](https://img.shields.io/badge/Backend-Python%20FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Grafana](https://img.shields.io/badge/Monitoring-Grafana-F46800?logo=grafana)](https://grafana.com/)
[![Live Demo](https://img.shields.io/badge/Live%20Portal-GitHub%20Pages-181717?logo=github)](https://henry-ibe.github.io/hipaa-hospital-system/)

---

## 📌 What Is This Project?

This project simulates a **real-world hospital IT infrastructure** running across multiple AWS regions. It was built to demonstrate the kind of systems a DevOps or Cloud Engineer would design and operate for a healthcare organization — including automated deployments, observability, and access control.

**Think of it like this:** instead of clicking through the AWS console to spin up servers manually, this system lets you deploy a fully configured hospital environment — with monitoring, security, and regional customization — using a single command.

---

## 🗺️ Architecture Overview

```
┌─────────────────────────────────────────────────┐
│              GitHub Pages Portal                │
│         (Self-Service Deployment UI)            │
└──────────────────┬──────────────────────────────┘
                   │ triggers
┌──────────────────▼──────────────────────────────┐
│              GitHub Actions CI/CD               │
│         (Automated Terraform Pipelines)         │
└──────┬───────────┬──────────────────────────────┘
       │           │
┌──────▼──┐   ┌────▼──────┐   ┌──────────────┐
│  AWS    │   │   AWS     │   │    AWS       │
│   NY    │   │    CA     │   │     IL       │
│(Urban)  │   │(Research) │   │ (Teaching)   │
└──────┬──┘   └─────┬─────┘   └──────┬───────┘
       │             │                │
       └─────────────▼────────────────┘
                     │
        ┌────────────▼─────────────┐
        │  Prometheus + Grafana    │
        │  (Unified Observability) │
        └──────────────────────────┘
```

Each AWS region runs:
- **EC2 instances** provisioned via Terraform
- **FastAPI backend** serving patient, bed, and cost data
- **Node Exporter** for infrastructure metrics
- **Region-specific configurations** (staffing, pricing, specialties)

---

## 🏗️ Key Components

### 1. Infrastructure as Code (`main.tf`, `variables.tf`)
All AWS infrastructure is defined in Terraform. You can spin up or tear down an entire hospital region in minutes.

### 2. FastAPI Backend (`app/`, `hospital-app/`)
A Python REST API that serves hospital data — patient volumes, bed occupancy, cost metrics — with JWT authentication and TOTP-based MFA.

### 3. Self-Service Deployment Portal (`deployment-portal/`)
A web UI (live on GitHub Pages) that allows one-click deployment of any hospital region without touching the command line. Backed by AWS Lambda.

### 4. Lambda Deployment API (`lambda-deployment-api/`)
Serverless API that receives deployment requests from the portal and triggers the appropriate Terraform workspace.

### 5. Monitoring Stack
- **Prometheus** scrapes metrics from all regions
- **Grafana dashboards** (`grafana-hospital-dashboard.json`, `hospital-dashboard.json`) visualize patient satisfaction, bed occupancy, cost per transaction, and system health in real time

### 6. CI/CD Pipeline (`.github/workflows/`)
GitHub Actions automates infrastructure validation and deployment.

---

## 🌍 Region Profiles

Each region has a unique configuration that reflects real-world hospital demographics and specialties.

| Region | Hospital Model | Focus | Pricing |
|---|---|---|---|
| 🗽 New York | Urban High-Volume (Mount Sinai) | Emergency, Trauma | +30% NYC premium |
| 🌴 California | Research Hospital (UCLA) | Surgery, Radiology | Standard |
| 🏙️ Illinois | Teaching Hospital (Northwestern) | Cardiology, Education | -10% Midwest |

Patient volumes, satisfaction targets, and cost structures are all region-specific — making this a realistic multi-tenant infrastructure simulation.

---

## 🛡️ Security Features

- **JWT Authentication** — stateless token-based API access
- **TOTP / MFA** — time-based one-time password support
- **Rate Limiting** — API abuse prevention
- **HIPAA-Aligned Design** — access controls, audit logging patterns, and data handling practices reflecting healthcare compliance requirements

---

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| Cloud | AWS (EC2, VPC, Lambda, IAM) |
| IaC | Terraform |
| Backend | Python, FastAPI, SQLite |
| Monitoring | Prometheus, Grafana, Node Exporter |
| Auth | JWT, TOTP |
| CI/CD | GitHub Actions |
| Frontend | HTML/CSS/JavaScript (GitHub Pages) |

---

## 🚀 Deployment

### Option 1: Self-Service Portal (No CLI needed)
Visit the live portal: **[henry-ibe.github.io/hipaa-hospital-system](https://henry-ibe.github.io/hipaa-hospital-system/)**

Select a region and click deploy — the portal handles everything via the Lambda API.

### Option 2: Terraform CLI

```bash
# Clone the repo
git clone https://github.com/henry-ibe/hipaa-hospital-system.git
cd hipaa-hospital-system

# Initialize Terraform
terraform init

# Deploy a specific region
terraform workspace new ny-hospital
terraform apply -var-file="ny-hospital.tfvars"

# Or deploy California
terraform workspace new ca-hospital
terraform apply -var-file="ca-hospital.tfvars"
```

**Prerequisites:** AWS CLI configured, Terraform >= 1.0, Python 3.9+

---

## 📊 Monitoring Dashboards

Once deployed, Grafana dashboards provide real-time visibility into:

- 🛏️ **Bed Occupancy** by department and region
- 😊 **Patient Satisfaction** scores (target: 4.5+ for CA research sites)
- 💰 **Cost Per Transaction** with regional pricing adjustments
- 💻 **System Health** — CPU, memory, disk across all EC2 instances

Dashboard JSON files are in the repo root and can be imported directly into any Grafana instance.

---

## 📁 Repository Structure

```
hipaa-hospital-system/
├── .github/workflows/       # CI/CD pipeline definitions
├── app/                     # Core FastAPI application
├── hospital-app/            # Hospital-specific app logic
├── deployment-portal/       # GitHub Pages self-service UI
├── lambda-deployment-api/   # Serverless deployment trigger
├── scripts/                 # Utility and automation scripts
├── main.tf                  # Primary Terraform configuration
├── variables.tf             # Input variable definitions
├── ny-hospital.tfvars       # New York region variables
├── ca-hospital.tfvars       # California region variables
├── tx-hospital.tfvars       # Texas region variables
├── grafana-hospital-dashboard.json   # Grafana dashboard config
└── PHASE4_WHITEPAPER.md     # Architecture deep-dive document
```

---

## 💡 What This Demonstrates

This project was built to showcase real DevOps and cloud engineering skills:

| Skill | How It's Demonstrated |
|---|---|
| Infrastructure as Code | Full Terraform configuration for multi-region AWS |
| CI/CD | GitHub Actions pipeline with automated deployments |
| Observability | Prometheus + Grafana with custom dashboards |
| Security | JWT, MFA, rate limiting, HIPAA design patterns |
| Self-Service Platforms | No-code deployment portal via GitHub Pages + Lambda |
| Multi-Region Architecture | Isolated workspaces, region-specific configs |
| API Design | FastAPI with authentication, business logic, metrics |

---

## 📄 Architecture Whitepaper

For a deep-dive into the design decisions, infrastructure patterns, and HIPAA considerations, see [`PHASE4_WHITEPAPER.md`](./PHASE4_WHITEPAPER.md).

---

## 👤 Author

**Henry Ibe** — Systems & Cloud Infrastructure Engineer  
[![GitHub](https://img.shields.io/badge/GitHub-henry--ibe-181717?logo=github)](https://github.com/henry-ibe)

---

*This is a portfolio/lab project. No real patient data is used or stored.*

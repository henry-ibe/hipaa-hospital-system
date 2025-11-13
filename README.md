# 🏥 Multi-Region Hospital Management System

Production-grade self-service hospital management platform with multi-region deployment and dynamic business metrics.

## 🌟 Features

- **Self-Service Portal**: One-click deployments via [GitHub Pages](https://henry-ibe.github.io/hipaa-hospital-system/)
- **Multi-Region**: NY (Urban), CA (Research), IL (Teaching) with unique profiles
- **Dynamic Metrics**: Region-specific patient volumes, costs, satisfaction scores
- **Elite Monitoring**: Prometheus + Grafana with business intelligence
- **Security**: JWT auth, MFA (TOTP), rate limiting, HIPAA-ready features

## 🗺️ Region Profiles

**New York (Mount Sinai)** - Urban High-Volume
- 50% more patients, Emergency focus, NYC pricing (+30%)

**California (UCLA)** - Research Hospital  
- Surgery/Radiology focus, Best satisfaction (4.5-4.8)

**Illinois (Northwestern)** - Teaching Hospital
- Cardiology focus, Best efficiency, Midwest pricing (-10%)

## 🛠️ Tech Stack

- Terraform, AWS EC2/VPC
- Python FastAPI, SQLite
- Prometheus, Grafana, Node Exporter
- JWT + TOTP authentication

## 🚀 Quick Start

Visit: https://henry-ibe.github.io/hipaa-hospital-system/

Or deploy via Terraform:
```bash
terraform init
terraform workspace new ny-hospital
terraform apply -var-file="ny-hospital.tfvars"
```

## 📊 Monitoring

- Patient satisfaction by region
- Bed occupancy by department  
- Cost per transaction with regional pricing
- System health and infrastructure metrics

## 🎯 Portfolio Value

Demonstrates: Multi-region architecture, self-service platforms, business metrics, IaC, production monitoring, security best practices.

Perfect for DevOps/SRE/Platform Engineering roles ($150K-250K+).

---

**Author**: Henry Ibe | [GitHub](https://github.com/henry-ibe)

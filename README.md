# Cloud-Native-MLOps
An automated, resilient, cloud-native machine learning serving platform designed for real-time e-commerce price optimization and demand forecasting. This project bridges data science model lifecycle management with production platform engineering across containerization, Infrastructure as Code (IaC), configuration management, GitOps CI/CD, container orchestration, end-to-end testing, centralized observability, and automated retraining loops.

---

## Architecture Overview

```text
[ Git Push / PR ] ──> [ GitHub Repository ]
                              │ (Webhook Trigger)
                              ▼
┌───────────────────── Jenkins CI/CD Pipeline ───────────────────────┐
│ 1. Code Checkout & Dependency Setup                                │
│ 2. SonarQube SAST & Quality Gate Enforcement                       │
│ 3. Multi-Stage Docker Image Build & Tagging                         │
│ 4. Push Container Image to Registry                                │
│ 5. Rolling Update Deployment to Kubernetes                          │
│ 6. Automated Selenium End-to-End Testing (Screenshots on Failure)  │
└─────────────────────────────┬──────────────────────────────────────┘
                              │
                              ▼
┌────────────────── Kubernetes Cluster ──────────────────────────────┐
│                                                                    │
│  [ Ingress Controller (SSL/TLS Termination & Path-Based Routing) ] │
│                  │                                                 │
│         ┌────────┴────────┐                                        │
│         ▼                 ▼                                        │
│  [ Frontend UI Pods ]   [ Flask + PyCaret ML Pods ] (HPA Scaling)  │
│                                │                                   │
└────────────────────────────────┼───────────────────────────────────┘
                                 │ (JSON Telemetry & Inference Logs)
                                 ▼
┌────────────────────────── ELK Stack ───────────────────────────────┐
│ [ Logstash ] ──> [ Elasticsearch Index ] ──> [ Kibana Dashboards ] │
└────────────────────────────────┬───────────────────────────────────┘
                                 │ (Drift Monitoring Query)
                                 ▼
                     [ Python Script / Cron Job ]
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
       [ ChatOps Webhook Alert ]     [ Jenkins Retrain Job ]
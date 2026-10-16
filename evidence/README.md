# Submission evidence

Screenshots and the recorded walkthrough for the capstone submission. AWS account identifiers are blacked out in the console screenshots; the raw Terraform logs (`terraform-aws-*.txt`) stay local because they contain the account ID.

| Rubric | File | Shows |
|---|---|---|
| **M10 Presentation** | **`StockPilot-demo-walkthrough.mp4`** | **Recorded walkthrough (7 min 36 s) of all 15 demo steps, including a live commit → CI pipeline → Argo CD deployment update** |
| M1 Application | `M1-api-docs-swagger.png` | FastAPI Swagger with all endpoints |
| M1 / M4 | `M4-browser-localhost-3000.png` | App running from Docker Compose |
| M2 Testing | `M2-pytest-all-passing.png` | `pytest -v`: 25 passed |
| M3 Git | `M3-git-commit-history.png` | Commit history (20+ meaningful commits) |
| M4 Docker | `M4-docker-compose-up.png` | `docker compose up --build`: all services healthy |
| M5 CI/CD | `M5-github-actions-runs.png` | Green pipeline runs on `main` (link: https://github.com/whenommmm/stockpilot/actions) |
| M5 CI/CD | https://github.com/users/whenommmm/packages/container/package/stockpilot-backend | GHCR package with commit-SHA tags |
| M6 Trivy | `M6-trivy-backend-scan.png`, `M6-trivy-frontend-scan.png` | Trivy step output: 0 fixable HIGH/CRITICAL |
| M7 Terraform | `M7-terraform-aws-plan.png` | Real `terraform plan` against AWS: 61 to add |
| M7 Terraform | `M7-terraform-aws-apply.png` | `terraform apply` complete (VPC + EKS in ap-south-1) |
| M7 Terraform | `M7-eks-nodes-ready.png` | `kubectl get nodes` on EKS: worker nodes Ready |
| M7 Terraform | `M7-console-vpc.png`, `M7-console-subnets.png` | AWS Console (Mumbai): `stockpilot-eks-vpc` + 2 public / 2 private subnets |
| M7 Terraform | `M7-console-eks-cluster.png`, `M7-console-eks-node-groups.png` | AWS Console: EKS `stockpilot-eks` Active (1.35), node group with 2 nodes Active |
| M7 Terraform | `M7-terraform-aws-destroy.png` | `terraform destroy` complete |
| M7 Terraform | `M7-terraform-aws-validate-test.png` | `validate` + `terraform test` (mocked AWS) |
| M8 K8s + Helm | `M8-kubectl-get-pods-svc.png` | Pods Running, ClusterIP Services, Ingress, HPA |
| M8 K8s + Helm | `M8-helm-upgrade-install.png` | `helm upgrade --install` → `helm list -n stockpilot-helm` (deployed) + pods Running |
| M8 K8s + Helm | `M8-helm-list-argocd.png` | Helm releases + Argo CD application Synced/Healthy |
| M8 K8s + Helm | `M8-app-via-ingress.png` | App at `stockpilot.localhost:8080` through the Ingress |
| M9 Observability | `M9-metrics-endpoint.png` | `/metrics` output |
| M9 Observability | `M9-prometheus-targets.png` | `stockpilot-backend` targets 2/2 UP |
| M9 Observability | `M9-grafana-dashboard.png` | Grafana dashboard with live data |

**Trivy explanation (M6):** see the "Trivy: what to say" section in `docs/DEMO_SCRIPT.md`.

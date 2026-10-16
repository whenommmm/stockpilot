# StockPilot — Build Plan

> **Status (2026-10-16):** every phase below is built and verified on the local cluster. CI is green
> on `main`, and Argo CD deploys each commit automatically. See the [README](../README.md) for how
> to run it, and [DEMO_SCRIPT.md](DEMO_SCRIPT.md) for the presentation.

This plan turns the Session 21 capstone brief (TaskBoard reference + `GRADING.md`) into an
ordered build for **StockPilot**, an inventory-management app. Each phase lists what gets built,
how to verify it, and the evidence the rubric asks for.

## Ground rules

- **Own domain.** TaskBoard is only an architectural reference. StockPilot has a different data
  model (products + stock movements), different API and different UI.
- **Zero cloud spend.** Everything runs on a local [kind](https://kind.sigs.k8s.io/) cluster
  created by Terraform. The AWS VPC + EKS code is written and validated, never applied.
- **Fix the reference's known bugs** (broken HCL, failing test, Compose start-up race, root
  nginx, hard-coded upstream, wrong Ingress service names, compromised Trivy action tag).
- **GitOps deploys.** CI never talks to the cluster. It pushes images and commits the new image
  tag; Argo CD inside the cluster pulls the change.

## Architecture

```text
 Developer ──git push──▶ GitHub ──▶ GitHub Actions
                                     ├─ ruff + pytest (SQLite)       ┐
                                     ├─ alembic upgrade/check (PG)   ├─ quality gates
                                     ├─ npm ci + vite build          ┘
                                     ├─ docker build ×2 ─▶ Trivy (fail on HIGH/CRITICAL)
                                     ├─ push ghcr.io/<owner>/stockpilot-{backend,frontend}:<sha>
                                     └─ commit imageTag=<sha> → helm/stockpilot/values-local.yaml
                                                     │
 Terraform ─▶ kind cluster (local)                   │ Argo CD polls the repo
   ├─ Traefik (Ingress)        ◀─────────────────────┘
   ├─ metrics-server (HPA)        Argo CD syncs the Helm chart:
   ├─ kube-prometheus-stack         Postgres (StatefulSet + PVC)
   └─ Argo CD                       migrate Job (alembic + seed)
                                    backend ×2..6 (HPA)  ◀── /api  ┐
                                    frontend ×2          ◀── /     ├─ Ingress stockpilot.localhost
                                    ServiceMonitor ─▶ Prometheus ─▶ Grafana dashboard
```

## Rubric map

| Module | Points | Where it lives | Risk |
|---|---|---|---|
| M1 Application | 10 | `backend/`, `frontend/` | — |
| M2 Testing | 10 | `backend/tests/`, `pytest.ini`, ruff | — |
| M3 Git/GitHub | 5 | history, `.gitignore` | needs ≥ 10 meaningful commits |
| M4 Docker | 10 | `*/Dockerfile`, `docker-compose.yml` | — |
| M5 CI/CD | 15 | `.github/workflows/ci-cd.yml` | — |
| M6 Trivy | 5 | same workflow | — |
| M7 Terraform | 15 | `terraform/local`, `terraform/aws` | **~7 pts (VPC/EKS provisioned) lost by design** unless kind is accepted |
| M8 K8s + Helm | 15 | `k8s/`, `helm/stockpilot/` | — |
| M9 Observability | 10 | `monitoring/`, ServiceMonitor, dashboard | — |
| M10 Presentation | 5 | `README.md`, `docs/DEMO_SCRIPT.md` | — |

## Phase 0 — Tooling

- [x] Docker (Colima/Docker Desktop, ≥ 6 GB RAM), Terraform ≥ 1.9, Helm 3/4, kubectl, Node 22+, `hey`
- [x] `gh auth login` (GitHub CLI)

## Phase 1 — Backend (M1, M2)

- [x] SQLAlchemy models `products`, `stock_movements`; quantity changes only through movements (audit trail)
- [x] Alembic migrations `0001_products`, `0002_stock_movements`
- [x] Endpoints: `/health`, `/ready` (DB check, 503 when down), `/metrics`, `/api/info`,
      products CRUD, `POST /api/products/{id}/adjust`, `GET /api/movements`, `GET /api/stats`
- [x] Custom metrics: `stockpilot_stock_adjustments_total{reason}`, `stockpilot_low_stock_products`,
      `stockpilot_out_of_stock_products`, `stockpilot_inventory_value`
- [x] Seed script with demo products (idempotent)
- [x] Tests first: ≥ 15 cases over every endpoint, isolated SQLite DB per test, `conftest.py` + `pytest.ini`
- **Verify:** `pytest -v` green, `ruff check .` clean
- **Evidence:** screenshot of `pytest -v`

## Phase 2 — Frontend (M1)

- [x] React + Vite, pinned versions, committed `package-lock.json`
- [x] KPI cards, product table (search, category + status filters, stock bars), create/edit/delete
      dialogs, adjust-stock dialog, live activity feed, loading/error states, responsive layout
- [x] Shows UI build SHA and API build SHA (makes the live-deploy demo visible)
- **Verify:** `npm run build`, manual check against the backend

## Phase 3 — Containers (M4)

- [x] Backend: multi-stage, venv, UID 10001, no migrations at start-up
- [x] Frontend: Node build stage → `nginx-unprivileged` (UID 101, port 8080), upstream from `BACKEND_URL`
- [x] Compose: Postgres healthcheck → one-shot `migrate` service → backend (healthcheck) → frontend
- **Verify:** `docker compose up --build` from an empty volume, all services healthy, UI at <http://localhost:3000>
- **Evidence:** compose output, browser at :3000, `docker compose exec postgres psql … -c '\dt'`

## Phase 4 — Git and GitHub (M3)

- [x] One commit per logical step (conventional messages), public repo `stockpilot`
- [x] `.gitignore` covers `.env`, `__pycache__`, `node_modules`, `.venv`, Terraform state
- **Evidence:** commit history screenshot (≥ 10 commits)

## Phase 5 — CI/CD + DevSecOps (M5, M6)

- [x] Jobs: `backend-test` (ruff, pytest), `migrations` (Postgres service, upgrade → check → downgrade → upgrade),
      `frontend-build`, `images` (matrix build → Trivy → push on `main`), `gitops-deploy`
- [x] Every third-party action pinned to a commit SHA; Trivy action ≥ v0.35.0 (CVE-2026-33634)
- [x] Image tags = full commit SHA, lowercase owner
- **Evidence:** green run URL, Trivy log, GHCR package page with SHA tags, 2–3 sentence Trivy explanation

## Phase 6 — Terraform (M7)

- [x] `terraform/local`: kind cluster (`tehcyx/kind`), ports 8080/8443 → Traefik NodePorts
- [x] `terraform/aws`: VPC (2 public + 2 private subnets, ELB tags, single NAT) + EKS (managed node
      group, EBS CSI driver with default gp3 StorageClass, metrics-server) — validated + mock-tested only
- [x] `terraform.tfvars.example` in both
- **Evidence:** `init` / `plan` / `apply` / `destroy` of `local`; `validate` + `terraform test` of `aws`

## Phase 7 — Kubernetes + Helm (M8)

- [x] `k8s/namespace.yaml`
- [x] Chart: Secret, Postgres StatefulSet + PVC (`PGDATA` subdir), migrate Job (Argo sync wave −1),
      backend + frontend Deployments (2 replicas, probes, non-root, resources), ClusterIP Services,
      Traefik Ingress (`/api` → backend, `/` → frontend), HPA (2–6 on CPU), ServiceMonitor, PrometheusRule,
      Grafana dashboard ConfigMap
- **Verify:** `helm lint`, `helm template`, deploy, all pods `Running`, app at <http://stockpilot.localhost:8080>
- **Evidence:** `kubectl get pods,svc -n stockpilot`, `helm list` / Argo CD app, browser via Ingress

## Phase 8 — GitOps (M5, M10)

- [x] Argo CD (Helm), `k8s/argocd-application.yaml` (auto-sync, prune, self-heal)
- [x] CI bumps `imageTag` in `values-local.yaml` → Argo CD rolls out
- **Evidence:** live demo — commit → pipeline → Argo CD sync → new build SHA in the UI

## Phase 9 — Observability (M9)

- [x] kube-prometheus-stack (Prometheus + Grafana, Ingress hosts `prometheus.localhost`, `grafana.localhost`)
- [x] Dashboard: request rate, p95 latency, 5xx ratio, backend replicas, CPU per pod, inventory KPIs
- [x] `scripts/load-test.sh` drives the HPA
- **Evidence:** `curl …/metrics`, Prometheus Targets page (UP), Grafana dashboard, `kubectl get hpa -w`

## Phase 10 — Troubleshooting lab

- [x] `troubleshooting/`: bad image tag, Service selector typo, broken readiness probe — each with
      symptoms, commands, root cause and fix

## Phase 11 — Documentation and demo (M10)

- [x] `README.md`: what the app does, architecture, local run, CI/CD, K8s, monitoring, rubric map
- [x] `docs/DEMO_SCRIPT.md`: the 15-step final demo plus screenshot checklist

## Clean-up

`terraform -chdir=terraform/local destroy` removes the whole cluster. Nothing in AWS is ever created.

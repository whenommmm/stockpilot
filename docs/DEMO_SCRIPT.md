# Final demo script

A run-through of the Session 21 final demo (README "Part O"), in order, with the exact commands,
followed by the screenshot checklist from `GRADING.md`.

## Before you start (5 minutes before)

```bash
docker info >/dev/null && echo "Docker OK"
kubectl config use-context kind-stockpilot
kubectl get pods -A | grep -v Running            # should print only the header and Completed jobs
```

If the cluster is gone, rebuild it: `terraform -chdir=terraform/local apply && ./scripts/platform-up.sh && kubectl apply -f k8s/argocd-application.yaml`.

Open these tabs: the app, Argo CD, Grafana, Prometheus targets, GitHub Actions, the GHCR packages page.

## The 15 steps

| # | Show | How |
|---|---|---|
| 1 | **Application** | <http://stockpilot.localhost:8080>: add a product, then *Adjust → Sale* until it goes **Low stock**; try to oversell and show it's refused |
| 2 | **API** | <http://stockpilot.localhost:8080/docs>: `GET /api/products`, `POST /api/products/{id}/adjust`, `GET /api/stats` |
| 3 | **Database** | `kubectl exec -n stockpilot stockpilot-postgres-0 -- psql -U stockpilot -c 'select sku, quantity from products' -c 'select * from stock_movements order by id desc limit 5'` |
| 4 | **Git** | Make a visible change (e.g. the heading in `frontend/src/App.jsx`), then `git commit -am "feat(ui): ..." && git push` |
| 5 | **CI** | GitHub → Actions: lint + tests, migration check and frontend build run in parallel |
| 6 | **Docker** | The `Image · backend` / `Image · frontend` jobs, plus `backend/Dockerfile` (multi-stage, UID 10001) and `frontend/Dockerfile` (Node build → non-root nginx) |
| 7 | **Security** | The Trivy step output in the image jobs (explanation below) |
| 8 | **Registry** | GitHub profile → Packages → `stockpilot-backend`: tags are commit SHAs |
| 9 | **Terraform** | `terraform/local` (applied) and `terraform/aws` (VPC + EKS); run `terraform -chdir=terraform/aws test` |
| 10 | **Kubernetes** | `kubectl get pods,svc -n stockpilot -o wide` |
| 11 | **Helm / GitOps** | `helm template` the chart; Argo CD UI shows the app *Synced / Healthy*; the deploy commit from step 4 rolls out, and the sidebar build SHA changes |
| 12 | **Ingress** | `kubectl get ingress -n stockpilot`: one host, `/api` → backend, `/` → frontend |
| 13 | **HPA** | `kubectl get hpa -n stockpilot -w` while `./scripts/load-test.sh` runs: replicas go from 2 towards 6 |
| 14 | **Monitoring** | Prometheus → Status → Targets (`stockpilot-backend` UP); Grafana → *StockPilot · Service & Inventory* |
| 15 | **Failure simulation** | `kubectl apply -f troubleshooting/broken-service.yaml`, then diagnose it live (see `troubleshooting/README.md`) |

## Trivy: what to say (M6)

> Trivy scans each image's OS packages (Debian or Alpine) and language dependencies (Python
> packages) against vulnerability databases, and the pipeline fails if it finds a HIGH or
> CRITICAL vulnerability that already has a fix. The first scan of the backend image found 4 HIGH
> CVEs, in `urllib3` and `msgpack` bundled inside `pip` and in a `setuptools` record. The app
> never uses pip at runtime, so the fix was to remove it from the final image rather than ignore
> the findings. Both images now scan clean. A clean scan means "no known, fixable HIGH/CRITICAL
> CVEs today", not "secure": it is one layer, alongside dependency updates (Dependabot), secret
> scanning, SHA-pinned actions and runtime controls (non-root, restricted Pod Security).

## Screenshot checklist (from GRADING.md)

Save them in a folder, e.g. `evidence/`, named by module.

**M1 Application**

- [ ] App in the browser (Compose: `localhost:3000`)

**M2 Testing**

- [ ] `pytest -v` with 25 passing tests

**M3 Git**

- [ ] Commit history (`git log --oneline`), at least 10 commits

**M4 Docker**

- [ ] `docker compose up --build` output
- [ ] Browser at `localhost:3000`

**M5 CI/CD**

- [ ] Green Actions run (URL)
- [ ] GHCR package page showing SHA tags

**M6 Trivy**

- [ ] Trivy step output
- [ ] The explanation above

**M7 Terraform**

- [ ] `terraform plan` / `apply` / `destroy` for `terraform/aws` (real AWS, ap-south-1)
- [ ] AWS Console: VPC, subnets, EKS cluster (Active), node group (2 nodes)
- [ ] `terraform validate` + `terraform test` for `terraform/aws`

**M8 Kubernetes + Helm**

- [ ] `kubectl get pods -n stockpilot` (all Running)
- [ ] `kubectl get svc -n stockpilot`
- [ ] `helm list -A` / Argo CD app view
- [ ] App through `stockpilot.localhost:8080`

**M9 Observability**

- [ ] `/metrics` output: `kubectl port-forward -n stockpilot svc/stockpilot-backend 8000:8000`, then `curl -s localhost:8000/metrics | grep stockpilot_` (`/metrics` is deliberately not exposed through the Ingress)
- [ ] Prometheus Targets page (UP)
- [ ] Grafana dashboard with live data

**M10 Presentation**

- [ ] `README.md`
- [ ] Live demo: commit → pipeline → deployment updates

> **Note on M7:** the AWS stack was applied on an AWS Free plan account, which cannot be charged,
> then destroyed. All the screenshots are in the git-ignored `evidence/` folder.

#!/usr/bin/env bash
# Installs the cluster add-ons StockPilot relies on into the kind cluster created by
# terraform/local: Traefik, metrics-server, kube-prometheus-stack and Argo CD.
# Safe to re-run: every step is an idempotent `helm upgrade --install`.
set -euo pipefail

CONTEXT="${CONTEXT:-kind-stockpilot}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

TRAEFIK_CHART_VERSION=41.7.1
METRICS_SERVER_CHART_VERSION=3.14.0
KUBE_PROMETHEUS_STACK_CHART_VERSION=92.9.0
ARGO_CD_CHART_VERSION=10.10.5

helm_install() {
  local release=$1 chart=$2 version=$3 namespace=$4 values=$5
  echo "==> ${release} (${chart} ${version}) -> namespace ${namespace}"
  helm --kube-context "$CONTEXT" upgrade --install "$release" "$chart" \
    --version "$version" --namespace "$namespace" --create-namespace \
    --values "$ROOT/$values" --wait --timeout 10m
}

echo "==> Preflight: inotify limits in the Docker VM"
# kind needs more inotify instances than Docker VMs allow by default; otherwise kube-proxy
# crash-loops with "too many open files" and Services stop routing.
instances=$(docker run --rm alpine:3 cat /proc/sys/fs/inotify/max_user_instances)
if [ "$instances" -lt 512 ]; then
  cat >&2 <<EOF
fs.inotify.max_user_instances is ${instances}; kind needs at least 512. Raise it, then re-run:
  colima ssh -- sudo sysctl -w fs.inotify.max_user_instances=512      # Colima
  docker run --rm --privileged alpine:3 sysctl -w fs.inotify.max_user_instances=512   # others
EOF
  exit 1
fi

echo "==> Helm repositories"
helm repo add traefik https://traefik.github.io/charts --force-update >/dev/null
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/ --force-update >/dev/null
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts --force-update >/dev/null
helm repo add argo https://argoproj.github.io/argo-helm --force-update >/dev/null
helm repo update >/dev/null

helm_install traefik traefik/traefik "$TRAEFIK_CHART_VERSION" traefik platform/traefik-values.yaml
helm_install metrics-server metrics-server/metrics-server "$METRICS_SERVER_CHART_VERSION" kube-system platform/metrics-server-values.yaml
helm_install kube-prometheus-stack prometheus-community/kube-prometheus-stack "$KUBE_PROMETHEUS_STACK_CHART_VERSION" monitoring monitoring/kube-prometheus-stack-values.yaml
helm_install argocd argo/argo-cd "$ARGO_CD_CHART_VERSION" argocd platform/argocd-values.yaml

echo "==> StockPilot namespace (Pod Security Standard: restricted)"
kubectl --context "$CONTEXT" apply -f "$ROOT/k8s/namespace.yaml"

argocd_password=$(kubectl --context "$CONTEXT" -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath='{.data.password}' | base64 --decode)

cat <<EOF

Platform ready:
  Grafana     http://grafana.localhost:8080     admin / stockpilot
  Prometheus  http://prometheus.localhost:8080
  Argo CD     http://argocd.localhost:8080      admin / ${argocd_password}

Next:
  kubectl apply -f k8s/argocd-application.yaml   # GitOps deploy from GitHub
  # or, without GitHub: ./scripts/load-local-images.sh && helm upgrade --install ...
EOF

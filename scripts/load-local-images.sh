#!/usr/bin/env bash
# Builds both images locally and loads them straight into the kind node, tagged exactly like
# the CI images but with the tag "dev" (the chart default). Useful before the first CI run,
# or to test a change without pushing it.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CLUSTER="${CLUSTER:-stockpilot}"
REGISTRY="${REGISTRY:-ghcr.io/whenommmm}"
TAG="${TAG:-dev}"

for component in backend frontend; do
  image="${REGISTRY}/stockpilot-${component}:${TAG}"
  echo "==> Building ${image}"
  docker build --quiet --build-arg "APP_VERSION=${TAG}" -t "$image" "$ROOT/$component" >/dev/null

  for node in $(docker ps --filter "label=io.x-k8s.kind.cluster=${CLUSTER}" --format '{{.Names}}'); do
    echo "    loading into ${node}"
    docker save "$image" | docker exec -i "$node" \
      ctr --namespace=k8s.io images import --all-platforms --digests --snapshotter=overlayfs - >/dev/null
  done
done
echo "Done. Images use imagePullPolicy IfNotPresent, so the cluster uses these copies."

#!/usr/bin/env bash
# Sends sustained traffic to the API through the Ingress so the backend's CPU rises above the
# HPA target (60% of its 100m request) and Kubernetes adds pods.
#
# Watch it in a second terminal:   kubectl get hpa,pods -n stockpilot -w
set -euo pipefail

DURATION="${DURATION:-180s}"
CONCURRENCY="${CONCURRENCY:-50}"
HOST_HEADER="${HOST_HEADER:-stockpilot.localhost}"
URL="${URL:-http://127.0.0.1:8080/api/products?q=e}"

if ! command -v hey >/dev/null; then
  echo "hey is not installed: brew install hey" >&2
  exit 1
fi

echo "Load: ${CONCURRENCY} concurrent clients for ${DURATION} against ${URL} (Host: ${HOST_HEADER})"
hey -z "$DURATION" -c "$CONCURRENCY" -host "$HOST_HEADER" "$URL"

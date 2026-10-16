# Troubleshooting lab

Three deliberately broken manifests, each a different, common failure. They live next to the real
app in the `stockpilot` namespace but are not part of the Helm chart, so Argo CD leaves them alone.

The general loop is always the same:

```text
kubectl get  →  kubectl describe  →  kubectl get events / logs  →  root cause  →  fix  →  verify
```

---

## 1. ImagePullBackOff: wrong image tag

```bash
kubectl apply -f troubleshooting/broken-image.yaml
kubectl get pods -n stockpilot -l app=lab-broken-image
```

**Symptom:** `STATUS` is `ErrImagePull`, then `ImagePullBackOff`. The container never starts.

**Investigate:**

```bash
kubectl describe pod -n stockpilot -l app=lab-broken-image    # read the Events section
kubectl get events -n stockpilot --sort-by=.lastTimestamp | tail
```

Events show `Failed to pull image "ghcr.io/whenommmm/stockpilot-backend:v9.9.9-does-not-exist" ... not found`.

**Root cause:** the tag doesn't exist in the registry. (The same symptom appears when a package
is private and there is no `imagePullSecret`; then the message says `401 Unauthorized`.)

**Fix:** point the Deployment at a tag that exists, e.g. the current commit SHA:

```bash
TAG=$(kubectl get deploy stockpilot-backend -n stockpilot -o jsonpath='{.spec.template.spec.containers[0].image}' | cut -d: -f2)
kubectl set image deploy/lab-broken-image -n stockpilot api=ghcr.io/whenommmm/stockpilot-backend:$TAG
kubectl rollout status deploy/lab-broken-image -n stockpilot
```

---

## 2. Service with no endpoints: selector typo

```bash
kubectl apply -f troubleshooting/broken-service.yaml
```

**Symptom:** the Service exists and has a ClusterIP, but nothing answers behind it.

**Investigate:**

```bash
kubectl get svc lab-broken-service -n stockpilot
kubectl get endpointslices -n stockpilot -l kubernetes.io/service-name=lab-broken-service   # no endpoints
kubectl describe svc lab-broken-service -n stockpilot | grep -E 'Selector|Endpoints'
kubectl get pods -n stockpilot --show-labels | grep component
```

**Root cause:** the selector asks for `app.kubernetes.io/component=api`, but the backend pods are
labelled `component=backend`. A Service routes only to pods whose labels match its selector:
no matching labels, no endpoints, no traffic.

**Fix:**

```bash
kubectl patch svc lab-broken-service -n stockpilot --type merge \
  -p '{"spec":{"selector":{"app.kubernetes.io/name":"stockpilot","app.kubernetes.io/component":"backend"}}}'
kubectl get endpointslices -n stockpilot -l kubernetes.io/service-name=lab-broken-service   # pod IPs appear
```

---

## 3. Running but never Ready: wrong readiness probe

```bash
kubectl apply -f troubleshooting/broken-readiness.yaml
kubectl get pods -n stockpilot -l app=lab-broken-readiness
```

**Symptom:** `STATUS` is `Running` but `READY` is `0/1`, and the Service has no ready endpoints.
Nothing crashes, which makes this one easy to miss.

**Investigate:**

```bash
kubectl describe pod -n stockpilot -l app=lab-broken-readiness | grep -A3 Readiness
kubectl get events -n stockpilot --field-selector reason=Unhealthy | tail -3
```

Events show `Readiness probe failed: ... dial tcp <pod-ip>:80: connect: connection refused`.

**Root cause:** the container listens on 8080 (non-root nginx can't bind to port 80), but the
probe checks port 80. Kubernetes keeps the pod out of the Service until the probe passes.

**Fix:** probe the named container port instead of a hard-coded number:

```bash
kubectl patch deploy lab-broken-readiness -n stockpilot --type json \
  -p '[{"op":"replace","path":"/spec/template/spec/containers/0/readinessProbe/httpGet/port","value":"http"}]'
kubectl get pods -n stockpilot -l app=lab-broken-readiness -w     # READY becomes 1/1
```

---

## Clean up

```bash
kubectl delete -f troubleshooting/ --ignore-not-found
```

## Bonus: break the real app and let GitOps heal it

```bash
kubectl scale deploy stockpilot-frontend -n stockpilot --replicas=0
kubectl get deploy stockpilot-frontend -n stockpilot -w
```

Argo CD's `selfHeal` notices that the live state no longer matches Git and restores 2 replicas
within seconds, without anyone running `kubectl`.

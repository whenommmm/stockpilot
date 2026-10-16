output "cluster_name" {
  value = kind_cluster.this.name
}

output "kubectl_context" {
  description = "kind adds this context to your kubeconfig and makes it current."
  value       = "kind-${kind_cluster.this.name}"
}

output "api_endpoint" {
  value = kind_cluster.this.endpoint
}

output "app_url" {
  value = "http://stockpilot.localhost:${var.ingress_http_port}"
}

output "next_step" {
  value = "./scripts/platform-up.sh   # installs Traefik, metrics-server, Prometheus/Grafana and Argo CD"
}

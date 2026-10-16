# A local Kubernetes cluster running in Docker (kind). This replaces the AWS VPC + EKS stack
# (../aws) for day-to-day work so the capstone costs nothing to run.
#
# Traffic path: browser -> localhost:8080 -> kind node port 30080 -> Traefik -> Services.

resource "kind_cluster" "this" {
  name           = var.cluster_name
  node_image     = var.node_image
  wait_for_ready = true

  kind_config {
    kind        = "Cluster"
    api_version = "kind.x-k8s.io/v1alpha4"

    node {
      role = "control-plane"

      extra_port_mappings {
        container_port = 30080
        host_port      = var.ingress_http_port
        listen_address = "127.0.0.1"
      }

      extra_port_mappings {
        container_port = 30443
        host_port      = var.ingress_https_port
        listen_address = "127.0.0.1"
      }
    }

    dynamic "node" {
      for_each = range(var.worker_count)

      content {
        role = "worker"
      }
    }
  }
}

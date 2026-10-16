variable "cluster_name" {
  description = "Name of the kind cluster (the kubectl context becomes kind-<name>)."
  type        = string
  default     = "stockpilot"
}

variable "node_image" {
  description = "kindest/node image, pinned by digest. Determines the Kubernetes version."
  type        = string
  default     = "kindest/node:v1.36.4@sha256:099e049362a1526b2db71494e1947aae99bd16290d7c895f2b7ea312e3cbfaed"
}

variable "worker_count" {
  description = "Extra worker nodes. 0 keeps a single node that runs everything (lightest for a laptop)."
  type        = number
  default     = 0

  validation {
    condition     = var.worker_count >= 0 && var.worker_count <= 3
    error_message = "worker_count must be between 0 and 3."
  }
}

variable "ingress_http_port" {
  description = "Host port mapped to the Traefik HTTP NodePort (30080)."
  type        = number
  default     = 8080
}

variable "ingress_https_port" {
  description = "Host port mapped to the Traefik HTTPS NodePort (30443)."
  type        = number
  default     = 8443
}

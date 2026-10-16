# Terraform

Two independent stacks:

| Stack | What it builds | Status |
|---|---|---|
| [`local/`](local) | A kind Kubernetes cluster in Docker, with host ports 8080/8443 wired to the ingress controller | **Applied**: the cluster the project runs on |
| [`aws/`](aws) | VPC (2 public + 2 private subnets, NAT gateway) and an EKS cluster with a managed node group, EBS CSI driver (default gp3 StorageClass) and metrics-server | **Validated and tested, never applied** (no cloud spend) |

## Local cluster (free)

```bash
cd terraform/local
terraform init
terraform plan                 # 1 to add: kind_cluster.this
terraform apply                # ~1 minute; switches kubectl to the kind-stockpilot context
kubectl get nodes
terraform destroy              # removes the whole cluster
```

## AWS stack (optional, costs money)

Checks that need no AWS account:

```bash
cd terraform/aws
terraform init -backend=false
terraform fmt -check -recursive
terraform validate
terraform test                 # plans the full stack against a mocked AWS provider
```

To create it for real, configure credentials (`aws configure` or SSO), then run
`terraform plan`, `terraform apply`, and afterwards
`aws eks update-kubeconfig --region ap-south-1 --name stockpilot-eks`. Run `terraform destroy` as
soon as you are done: the EKS control plane, NAT gateway and two `t3.medium` nodes are billed
by the hour.

Design notes:

- Worker nodes sit in **private** subnets and reach the internet through a single NAT gateway.
- Subnets carry the `kubernetes.io/role/elb` and `kubernetes.io/role/internal-elb` tags so
  load balancers are placed correctly.
- New EKS clusters have **no default StorageClass**, so the EBS CSI add-on is configured to create
  one. Without it the Postgres PVC would stay `Pending` forever.
- `kubernetes_version` defaults to a version in standard support. Extended-support versions cost
  six times as much per hour.

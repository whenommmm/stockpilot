# Terraform

Two independent stacks:

| Stack | What it builds | Status |
|---|---|---|
| [`local/`](local) | A kind Kubernetes cluster in Docker, with host ports 8080/8443 wired to the ingress controller | **Applied**: the cluster the project runs on |
| [`aws/`](aws) | VPC (2 public + 2 private subnets, NAT gateway) and an EKS cluster with a managed node group, EBS CSI driver (default gp3 StorageClass) and metrics-server | **Applied once, then destroyed**: 61 resources on an AWS Free plan account, paid from free credits |

## Local cluster (free)

```bash
cd terraform/local
terraform init
terraform plan                 # 1 to add: kind_cluster.this
terraform apply                # ~1 minute; switches kubectl to the kind-stockpilot context
kubectl get nodes
terraform destroy              # removes the whole cluster
```

## AWS stack (applied once, then destroyed)

Checks that need no AWS account:

```bash
cd terraform/aws
terraform init -backend=false
terraform fmt -check -recursive
terraform validate
terraform test                 # plans the full stack against a mocked AWS provider
```

To create it for real, configure credentials (`aws configure --profile ...` or SSO), then run
`terraform plan`, `terraform apply` (about 15–20 minutes), and afterwards
`aws eks update-kubeconfig --region ap-south-1 --name stockpilot-eks`. Run `terraform destroy` as
soon as you are done: the EKS control plane, NAT gateway and two nodes are billed by the hour.

This was done once for the capstone on an AWS **Free plan** account. A Free-plan account cannot be
charged; usage comes out of the sign-up credits.

- **Node size:** the Free plan only allows Free Tier eligible instance types, so the node group
  uses `c7i-flex.large` (2 vCPU, 4 GiB) instead of `t3.medium`.
- **vCPU quota:** new accounts get only 5 on-demand vCPUs, so set `node_max_size = 2` in
  `terraform.tfvars`.
- **Result:** `terraform plan` showed 61 to add, `apply` created the VPC, subnets, NAT gateway, EKS 1.35
  cluster and a 2-node group (both nodes `Ready`), and `destroy` removed all 61 resources.

Design notes:

- Worker nodes sit in **private** subnets and reach the internet through a single NAT gateway.
- Subnets carry the `kubernetes.io/role/elb` and `kubernetes.io/role/internal-elb` tags so
  load balancers are placed correctly.
- New EKS clusters have **no default StorageClass**, so the EBS CSI add-on is configured to create
  one. Without it the Postgres PVC would stay `Pending` forever.
- `kubernetes_version` defaults to a version in standard support. Extended-support versions cost
  six times as much per hour.

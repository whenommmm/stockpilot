# Production-style AWS infrastructure for StockPilot: a VPC across two availability zones and an
# EKS cluster with one managed node group. Applied once on an AWS Free plan account (ap-south-1) to
# verify it and capture the capstone evidence, then destroyed; day to day the project runs on the
# free local kind cluster in ../local.
#
#   VPC 10.20.0.0/16
#   ├── public subnets  (2 AZs)  internet gateway, NAT gateway, internet-facing load balancers
#   └── private subnets (2 AZs)  EKS worker nodes, internal load balancers
#         └── EKS control plane + managed node group (c7i-flex.large x2, scales to 4)

data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  azs = slice(data.aws_availability_zones.available.names, 0, 2)
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 6.7"

  name = "${var.cluster_name}-vpc"
  cidr = var.vpc_cidr
  azs  = local.azs

  private_subnets = [for index, _ in local.azs : cidrsubnet(var.vpc_cidr, 8, index + 1)]
  public_subnets  = [for index, _ in local.azs : cidrsubnet(var.vpc_cidr, 8, index + 101)]

  enable_nat_gateway   = true
  single_nat_gateway   = true # one NAT gateway instead of one per AZ keeps the bill down
  enable_dns_hostnames = true

  # Tags the AWS load balancer integration uses to discover subnets.
  public_subnet_tags  = { "kubernetes.io/role/elb" = 1 }
  private_subnet_tags = { "kubernetes.io/role/internal-elb" = 1 }
}

# IAM role the EBS CSI driver assumes through EKS Pod Identity, so PersistentVolumeClaims
# (the Postgres StatefulSet) can create EBS volumes.
module "ebs_csi_pod_identity" {
  source  = "terraform-aws-modules/eks-pod-identity/aws"
  version = "~> 2.9"

  name                      = "${var.cluster_name}-ebs-csi"
  attach_aws_ebs_csi_policy = true
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 21.29"

  name               = var.cluster_name
  kubernetes_version = var.kubernetes_version

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  endpoint_public_access                   = true
  enable_cluster_creator_admin_permissions = true

  addons = {
    vpc-cni                = { before_compute = true }
    eks-pod-identity-agent = { before_compute = true }
    kube-proxy             = {}
    coredns                = {}
    # Resource metrics for the HorizontalPodAutoscaler.
    metrics-server = {}
    aws-ebs-csi-driver = {
      pod_identity_association = [{
        role_arn        = module.ebs_csi_pod_identity.iam_role_arn
        service_account = "ebs-csi-controller-sa"
      }]
      # New EKS clusters have no default StorageClass; this adds a default gp3 one.
      configuration_values = jsonencode({ defaultStorageClass = { enabled = true } })
    }
  }

  eks_managed_node_groups = {
    default = {
      ami_type       = "AL2023_x86_64_STANDARD"
      instance_types = var.node_instance_types
      min_size       = var.node_min_size
      desired_size   = var.node_desired_size
      max_size       = var.node_max_size
    }
  }
}

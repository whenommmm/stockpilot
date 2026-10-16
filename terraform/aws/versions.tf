terraform {
  required_version = ">= 1.9.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  # For a team setup, keep state remotely, e.g.:
  # backend "s3" {
  #   bucket       = "my-terraform-state"
  #   key          = "stockpilot/eks.tfstate"
  #   region       = "ap-south-1"
  #   use_lockfile = true
  # }
}

# Credentials come from the environment (`aws configure`, AWS_PROFILE or SSO), never from code.
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "stockpilot"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

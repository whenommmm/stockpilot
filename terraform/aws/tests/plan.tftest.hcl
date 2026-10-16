# `terraform test` plans the whole AWS stack against a mocked AWS provider, so the configuration
# is exercised end to end without an AWS account, credentials or any cost.

mock_provider "aws" {
  mock_data "aws_availability_zones" {
    defaults = {
      names = ["ap-south-1a", "ap-south-1b", "ap-south-1c"]
    }
  }

  mock_data "aws_partition" {
    defaults = {
      partition  = "aws"
      dns_suffix = "amazonaws.com"
    }
  }

  mock_data "aws_caller_identity" {
    defaults = {
      account_id = "123456789012"
      arn        = "arn:aws:iam::123456789012:user/capstone"
    }
  }

  mock_data "aws_iam_session_context" {
    defaults = {
      issuer_arn = "arn:aws:iam::123456789012:user/capstone"
    }
  }

  mock_data "aws_iam_policy_document" {
    defaults = {
      json = "{\"Version\":\"2012-10-17\",\"Statement\":[]}"
    }
  }
}

run "vpc_spans_two_azs_with_public_and_private_subnets" {
  command = plan

  assert {
    condition     = tolist(output.public_subnet_cidrs) == tolist(["10.20.101.0/24", "10.20.102.0/24"])
    error_message = "Expected two public subnets, one per AZ."
  }

  assert {
    condition     = tolist(output.private_subnet_cidrs) == tolist(["10.20.1.0/24", "10.20.2.0/24"])
    error_message = "Expected two private subnets, one per AZ."
  }
}

run "eks_cluster_uses_the_requested_name_and_version" {
  command = plan

  assert {
    condition     = output.cluster_name == "stockpilot-eks"
    error_message = "Unexpected EKS cluster name."
  }

  assert {
    condition     = output.cluster_version == "1.35"
    error_message = "Unexpected Kubernetes version."
  }
}

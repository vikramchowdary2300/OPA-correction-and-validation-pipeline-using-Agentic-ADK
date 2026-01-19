terraform {
  required_providers {
    awscc = {
      source  = "hashicorp/awscc"
      version = "~> 0.1"
    }
    github = {
      source  = "integrations/github"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  default_tags {
    tags = local.default_tags
  }
  region     = var.region
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
}

provider "awscc" {
  region     = var.region
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
}

provider "github" {
  token = var.github_security_token
  owner = var.github_username
}
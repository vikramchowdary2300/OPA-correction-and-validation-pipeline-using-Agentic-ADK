locals {
  default_tags = {
    App    = var.application_name
    Branch = var.tf_branch
    Owner  = var.owner
    Repo   = var.repository_name
  }
}
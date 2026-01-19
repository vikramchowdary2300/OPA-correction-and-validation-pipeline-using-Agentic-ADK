data "github_repository" "terraform_repository" {
  name = var.repository_name
}

data "github_branch" "terraform_branch" {
  repository = data.github_repository.terraform_repository.name
  branch     = var.tf_branch
}
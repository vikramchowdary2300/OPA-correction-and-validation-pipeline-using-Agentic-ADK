resource "aws_codepipeline" "terraform_code_pipeline" {
  name           = "${var.application_name}-TerraformCodePipeline"
  role_arn       = aws_iam_role.codepipeline_role.arn
  pipeline_type  = "V2"
  execution_mode = "SUPERSEDED"
  artifact_store {
    type     = "S3"
    location = aws_s3_bucket.codepipeline_bucket.bucket
  }

  stage {
    name = "Source"
    action {
      name             = "Source"
      category         = "Source"
      owner            = "ThirdParty"
      provider         = "GitHub"
      version          = "1"
      run_order        = 1
      output_artifacts = ["source_output"]
      configuration = {
        Owner                = var.github_username
        Repo                 = data.github_repository.terraform_repository.name
        Branch               = data.github_branch.terraform_branch.branch
        OAuthToken           = var.github_security_token
        PollForSourceChanges = true
      }
    }
  }

  stage {
    name = "TerraformValidate"
    action {
      version          = "1"
      name             = "TerraformValidate"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = ["terraform_validate_output"]
      configuration = {
        ProjectName = aws_codebuild_project.terraform_validate_build_project.name
      }
    }
  }

  stage {
    name = "TerraformPlan"
    action {
      version          = "1"
      name             = "TerraformPlan"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = ["terraform_plan_output"]
      configuration = {
        ProjectName = aws_codebuild_project.terraform_plan_build_project.name
      }
    }
  }

  stage {
    name = "TerraformComplianceScan"
    action {
      version          = "1"
      name             = "TerraformComplianceScan"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["terraform_plan_output"]
      output_artifacts = ["terraform_compliance_scan_output"]
      configuration = {
        ProjectName = aws_codebuild_project.terraform_compliance_scan_build_project.name
      }
    }
  }

  stage {
    name = "ManualApproval"
    action {
      version  = "1"
      name     = "ManualApproval"
      category = "Approval"
      owner    = "AWS"
      provider = "Manual"
    }
  }

  stage {
    name = "TerraformApply"
    action {
      version          = "1"
      name             = "TerraformApply"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["terraform_plan_output"]
      output_artifacts = ["terraform_apply_output"]
      configuration = {
        ProjectName = aws_codebuild_project.terraform_apply_build_project.name
      }
    }
  }

}
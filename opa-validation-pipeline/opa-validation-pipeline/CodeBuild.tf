resource "aws_codebuild_project" "terraform_validate_build_project" {
  name         = "${var.application_name}-TerraformValidateBuild"
  service_role = aws_iam_role.codebuild_role.arn
  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type    = "BUILD_GENERAL1_SMALL"
    image           = "aws/codebuild/amazonlinux2-x86_64-standard:5.0"
    type            = "LINUX_CONTAINER"
    privileged_mode = true
  }

  source {
    type = "CODEPIPELINE"
    buildspec = templatefile("${path.module}/terraformValidateBuildspec.yml", {
      region            = var.region,
      TERRAFORM_VERSION = "1.5.7"
    })
  }
}

resource "aws_codebuild_project" "terraform_plan_build_project" {
  name         = "${var.application_name}-TerraformPlanBuild"
  service_role = aws_iam_role.codebuild_role.arn
  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type    = "BUILD_GENERAL1_SMALL"
    image           = "aws/codebuild/amazonlinux2-x86_64-standard:5.0"
    type            = "LINUX_CONTAINER"
    privileged_mode = true
  }

  source {
    type = "CODEPIPELINE"
    buildspec = templatefile("${path.module}/terraformPlanBuildspec.yml", {
      REGION            = var.region,
      TERRAFORM_VERSION = "1.5.7"
    })
  }
}

resource "aws_codebuild_project" "terraform_apply_build_project" {
  name         = "${var.application_name}-TerraformApplyBuild"
  service_role = aws_iam_role.codebuild_role.arn
  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type    = "BUILD_GENERAL1_SMALL"
    image           = "aws/codebuild/amazonlinux2-x86_64-standard:5.0"
    type            = "LINUX_CONTAINER"
    privileged_mode = true
  }

  source {
    type = "CODEPIPELINE"
    buildspec = templatefile("${path.module}/terraformApplyBuildspec.yml", {
      REGION            = var.region,
      TERRAFORM_VERSION = "1.5.7"
    })
  }
}

resource "aws_codebuild_project" "terraform_destroy_build_project" {
  name         = "${var.application_name}-TerraformDestroyBuild"
  service_role = aws_iam_role.codebuild_role.arn
  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type    = "BUILD_GENERAL1_SMALL"
    image           = "aws/codebuild/amazonlinux2-x86_64-standard:5.0"
    type            = "LINUX_CONTAINER"
    privileged_mode = true
  }

  source {
    type = "CODEPIPELINE"
    buildspec = templatefile("${path.module}/terraformDestroyBuildspec.yml", {
      REGION            = var.region,
      TERRAFORM_VERSION = "1.5.7"
    })
  }
}


resource "aws_codebuild_project" "terraform_compliance_scan_build_project" {
  name         = "${var.application_name}-TerraformComplianceScanBuild"
  service_role = aws_iam_role.codebuild_role.arn
  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type    = "BUILD_GENERAL1_SMALL"
    image           = "aws/codebuild/amazonlinux2-x86_64-standard:5.0"
    type            = "LINUX_CONTAINER"
    privileged_mode = true
  }

  source {
    type = "CODEPIPELINE"
    buildspec = templatefile("${path.module}/terraformComplianceScanBuildspec.yml", {
      REGION             = var.region,
      OPA_VERSION        = "1.2.0",
      POLICY_BUCKET      = aws_s3_bucket.policy_bucket.bucket,
      NOTIFICATION_EMAIL = aws_sns_topic_subscription.terraform_compliance_scan_sns_topic_subscription.endpoint,
      SNS_TOPIC_ARN      = aws_sns_topic.terraform_compliance_scan_sns_topic.arn
    })
  }
}
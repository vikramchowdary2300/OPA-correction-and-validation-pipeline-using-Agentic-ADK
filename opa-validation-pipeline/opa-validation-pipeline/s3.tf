resource "aws_s3_bucket" "codepipeline_bucket" {
  bucket        = "${var.application_name}-thesis-pipeline-bucket"
  force_destroy = true
}

resource "aws_s3_bucket_versioning" "codepipeline_bucket_versioning" {
  bucket = aws_s3_bucket.codepipeline_bucket.bucket
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket" "policy_bucket" {
  bucket        = "${var.application_name}-policy-bucket"
  force_destroy = true
}

resource "aws_s3_bucket_versioning" "policy_bucket_versioning" {
  bucket = aws_s3_bucket.policy_bucket.bucket
  versioning_configuration {
    status = "Enabled"
  }
}

locals {
  policy_files = fileset("${path.module}/policies/", "*.rego")
}

resource "aws_s3_object" "policy_files" {
  for_each = local.policy_files
  
  bucket = aws_s3_bucket.policy_bucket.bucket
  key    = "policies/${each.value}"
  source = "${path.module}/policies/${each.value}"
  etag   = filemd5("${path.module}/policies/${each.value}")
}
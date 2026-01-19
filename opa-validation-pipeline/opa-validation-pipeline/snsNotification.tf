resource "aws_sns_topic" "terraform_compliance_scan_sns_topic" {
  name = "${var.application_name}-TerraformComplianceScanSNS"
}

resource "aws_sns_topic_subscription" "terraform_compliance_scan_sns_topic_subscription" {
  topic_arn = aws_sns_topic.terraform_compliance_scan_sns_topic.arn
  protocol  = "email"
  endpoint  = var.email_id
}
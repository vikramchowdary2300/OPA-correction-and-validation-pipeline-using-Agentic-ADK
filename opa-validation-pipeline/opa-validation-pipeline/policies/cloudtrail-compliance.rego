package policies

import future.keywords.in

# Enforce CloudTrail logging
deny contains msg if {
	not has_cloudtrail
	msg = "CloudTrail must be enabled for the AWS account (PCI-DSS Req 10.1, HIPAA 164.312(b))"
}

has_cloudtrail if {
	some resource in input.planned_values.root_module.resources
	resource.type == "aws_cloudtrail"
}

# Ensure CloudTrail is properly configured
deny contains msg if {
	some resource in input.planned_values.root_module.resources
	resource.type == "aws_cloudtrail"
	not resource.values.enable_log_file_validation
	msg = sprintf("CloudTrail %v must have log file validation enabled (PCI-DSS Req 10.5, HIPAA 164.312(c)(2))", [resource.values.name])
}

deny contains msg if {
	some resource in input.planned_values.root_module.resources
	resource.type == "aws_cloudtrail"
	not resource.values.kms_key_id
	msg = sprintf(
		"CloudTrail %v must be encrypted using KMS (PCI-DSS Req 3.4, HIPAA 164.312(a)(2)(iv))",
		[resource.values.name],
	)
}

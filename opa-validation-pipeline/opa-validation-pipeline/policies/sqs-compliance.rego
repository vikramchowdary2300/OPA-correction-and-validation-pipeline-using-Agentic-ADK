package policies

import future.keywords.in

# Enforce encryption
deny contains msg if {
	some resource in input.planned_values.root_module.resources
	resource.type == "aws_sqs_queue"

	# Check if KMS key is missing or empty
	not resource.values.kms_master_key_id

	msg = sprintf(
		"SQS queue %v must be encrypted with KMS (PCI-DSS Req 3.4, HIPAA 164.312(a)(2)(iv))",
		[resource.values.name],
	)
}

# Enforce encryption (empty string case)
deny contains msg if {
	some resource in input.planned_values.root_module.resources
	resource.type == "aws_sqs_queue"

	# Check if KMS key is empty
	resource.values.kms_master_key_id == ""

	msg = sprintf(
		"SQS queue %v must be encrypted with KMS (PCI-DSS Req 3.4, HIPAA 164.312(a)(2)(iv))",
		[resource.values.name],
	)
}

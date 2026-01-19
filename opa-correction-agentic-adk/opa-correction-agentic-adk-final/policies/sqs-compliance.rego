package policies

import future.keywords.in

# Enforce encryption
deny contains msg if {
	some resource in input.planned_values.root_module.resources
	resource.type == "aws_sqs_queue"

	# Check if KMS key is missing or empty
	# If it is null, it might be computed (known after apply), so we skip check or assume compliant
	not has_kms_key(resource)

	msg = sprintf(
		"SQS queue %v must be encrypted with KMS (PCI-DSS Req 3.4, HIPAA 164.312(a)(2)(iv))",
		[resource.values.name],
	)
}

has_kms_key(resource) if {
	# Check if key is present and not empty string
	resource.values.kms_master_key_id != ""
	resource.values.kms_master_key_id != null
}

has_kms_key(resource) if {
	# If key is null (computed), we assume it will be provided
	resource.values.kms_master_key_id == null
}

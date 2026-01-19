package policies

import future.keywords.in

# Enforce key rotation
deny contains msg if {
	some resource in input.planned_values.root_module.resources
	resource.type == "aws_kms_key"
	not resource.values.enable_key_rotation
	msg = sprintf(
		"KMS key %v must have automatic rotation enabled (PCI-DSS Req 3.6.4, HIPAA 164.312(a)(2)(iv))",
		[resource.values.id],
	)
}

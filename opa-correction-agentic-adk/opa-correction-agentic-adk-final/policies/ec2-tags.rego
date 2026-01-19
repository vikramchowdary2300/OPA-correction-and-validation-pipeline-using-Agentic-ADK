package policies

import future.keywords.in

# Enforce encrypted EBS volumes
deny contains msg if {
	some resource in input.planned_values.root_module.resources
	resource.type == "aws_ebs_volume"
	encrypted := object.get(resource.values, "encrypted", false)
	not encrypted
	msg = sprintf("EBS volume %v must be encrypted (PCI-DSS Req 3.4, HIPAA 164.312(a)(2)(iv))", [resource.values.id])
}

# Helper function for metadata options - check if http_tokens is "required"
valid_metadata_options(options) if {
	is_array(options)
	some i
	options[i].http_tokens == "required"
}

valid_metadata_options(options) if {
	not is_array(options)
	options.http_tokens == "required"
}

# Enforce IMDSv2
deny contains msg if {
	some resource in input.planned_values.root_module.resources
	resource.type == "aws_instance"
	resource.values.metadata_options # Check metadata_options exists
	not valid_metadata_options(resource.values.metadata_options)
	msg = sprintf("EC2 instance %v must use IMDSv2 (required tokens) for improved security", [resource.values.id])
}

# Additional rule for missing metadata_options
deny contains msg if {
	some resource in input.planned_values.root_module.resources
	resource.type == "aws_instance"
	not resource.values.metadata_options # Missing metadata_options
	msg = sprintf("EC2 instance %v must use IMDSv2 (required tokens) for improved security", [resource.values.id])
}

# Enforce detailed monitoring
deny contains msg if {
	some resource in input.planned_values.root_module.resources
	resource.type == "aws_instance"
	not resource.values.monitoring
	msg = sprintf(
		"EC2 instance %v must have detailed monitoring enabled (PCI-DSS Req 10.2, HIPAA 164.308(a)(1)(ii)(D))",
		[resource.values.id],
	)
}

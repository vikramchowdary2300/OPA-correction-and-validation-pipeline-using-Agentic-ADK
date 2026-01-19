package policies

import future.keywords.in

# Enforce encryption
deny contains msg if {
	some resource in input.planned_values.root_module.resources
	resource.type == "aws_db_instance"
	not resource.values.storage_encrypted
	msg = sprintf(
		"RDS instance %v must have storage encryption enabled (PCI-DSS Req 3.4, HIPAA 164.312(a)(2)(iv))",
		[resource.values.identifier],
	)
}

# Enforce backup retention
deny contains msg if {
	some resource in input.planned_values.root_module.resources
	resource.type == "aws_db_instance"
	resource.values.backup_retention_period < 7
	msg = sprintf(
		"RDS %v must have a backup retention period of at least 7 days (PCI-DSS Req 9.5, HIPAA 164.308(a)(7))",
		[resource.values.identifier],
	)
}

# Enforce multi-AZ deployment
deny contains msg if {
	some resource in input.planned_values.root_module.resources
	resource.type == "aws_db_instance"
	not resource.values.multi_az
	msg = sprintf(
		"RDS instance %v must be configured for Multi-AZ deployment (HIPAA 164.308(a)(7))",
		[resource.values.identifier],
	)
}

# Enforce deletion protection
deny contains msg if {
	some resource in input.planned_values.root_module.resources
	resource.type == "aws_db_instance"
	not resource.values.deletion_protection
	msg = sprintf("RDS instance %v must have deletion protection enabled", [resource.values.identifier])
}

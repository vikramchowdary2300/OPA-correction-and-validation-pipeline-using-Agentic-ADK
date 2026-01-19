package policies

import future.keywords.in

# Enforce VPC flow logs
deny contains msg if {
	some resource in input.planned_values.root_module.resources
	resource.type == "aws_vpc"
	not has_flow_logs(resource.values.id)
	msg = sprintf("VPC %v must have flow logs enabled (PCI-DSS Req 10.2, HIPAA 164.312(b))", [resource.values.id])
}

has_flow_logs(vpc_id) if {
	some resource in input.planned_values.root_module.resources
	resource.type == "aws_flow_log"
	resource.values.vpc_id == vpc_id
}

# Allow if VPC ID is computed (null)
has_flow_logs(vpc_id) if {
	vpc_id == null
}

# Enforce secure Security Group rules
deny contains msg if {
	some resource in input.planned_values.root_module.resources
	resource.type == "aws_security_group_rule"
	resource.values.type == "ingress"
	some cidr in resource.values.cidr_blocks
	cidr == "0.0.0.0/0"
	resource.values.from_port <= 22
	resource.values.to_port >= 22
	msg = sprintf(
		"Security group rule %v allows SSH access from the internet (PCI-DSS Req 1.3, HIPAA 164.308(a)(3))",
		[resource.values.id],
	)
}

deny contains msg if {
	some resource in input.planned_values.root_module.resources
	resource.type == "aws_security_group_rule"
	resource.values.type == "ingress"
	some cidr in resource.values.cidr_blocks
	cidr == "0.0.0.0/0"
	resource.values.from_port <= 3389
	resource.values.to_port >= 3389
	msg = sprintf(
		"Security group rule %v allows RDP access from the internet (PCI-DSS Req 1.3, HIPAA 164.308(a)(3))",
		[resource.values.id],
	)
}

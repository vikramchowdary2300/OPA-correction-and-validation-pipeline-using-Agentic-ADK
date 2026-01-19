package policies

import future.keywords.in

# Check if a security group allows SSH access from 0.0.0.0/0 (open to internet)
deny contains msg if {
	resource := input.planned_values.root_module.resources[_]
	resource.type == "aws_security_group"
	ingress := resource.values.ingress[_]

	# Check if the port range includes SSH port 22
	from_port := ingress.from_port
	to_port := ingress.to_port
	from_port <= 22
	to_port >= 22

	# Check if CIDR blocks include 0.0.0.0/0 (open to internet)
	"0.0.0.0/0" in ingress.cidr_blocks

	msg = sprintf("Security group %v allows open SSH access (0.0.0.0/0)", [resource.values.name])
}

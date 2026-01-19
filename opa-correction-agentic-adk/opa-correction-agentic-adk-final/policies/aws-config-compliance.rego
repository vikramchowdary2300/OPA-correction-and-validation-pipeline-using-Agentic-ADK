package policies

import future.keywords.in

# Enforce AWS Config
deny contains msg if {
	not has_aws_config
	msg = "AWS Config must be enabled to monitor resource compliance (PCI-DSS Req 11.5, HIPAA 164.308(a)(1)(ii)(D))"
}

has_aws_config if {
	some resource in input.planned_values.root_module.resources
	resource.type == "aws_config_configuration_recorder"
}

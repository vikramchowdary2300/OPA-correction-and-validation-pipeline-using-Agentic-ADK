package policies

import future.keywords.in

# Enforce password policy
deny contains msg if {
	some resource in input.planned_values.root_module.resources
	resource.type == "aws_iam_account_password_policy"
	resource.values.minimum_password_length < 14
	msg = "IAM password policy must require a minimum of 14 characters (PCI-DSS Req 8.2.3)"
}

deny contains msg if {
	some resource in input.planned_values.root_module.resources
	resource.type == "aws_iam_account_password_policy"
	not resource.values.require_uppercase_characters
	msg = "IAM password policy must require uppercase characters (PCI-DSS Req 8.2.3)"
}

deny contains msg if {
	some resource in input.planned_values.root_module.resources
	resource.type == "aws_iam_account_password_policy"
	not resource.values.require_lowercase_characters
	msg = "IAM password policy must require lowercase characters (PCI-DSS Req 8.2.3)"
}

deny contains msg if {
	some resource in input.planned_values.root_module.resources
	resource.type == "aws_iam_account_password_policy"
	not resource.values.require_numbers
	msg = "IAM password policy must require numbers (PCI-DSS Req 8.2.3)"
}

deny contains msg if {
	some resource in input.planned_values.root_module.resources
	resource.type == "aws_iam_account_password_policy"
	not resource.values.require_symbols
	msg = "IAM password policy must require symbols (PCI-DSS Req 8.2.3)"
}

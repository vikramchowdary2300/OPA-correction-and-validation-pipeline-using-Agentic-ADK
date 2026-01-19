package policies

import future.keywords.in

deny contains msg if {
	resource := input.planned_values.root_module.resources[_]
	resource.type == "aws_iam_role"
	policy := json.unmarshal(resource.values.assume_role_policy)
	statement := policy.Statement[_]
	statement.Principal.AWS == "*"
	msg = sprintf("IAM role %v contains wildcard principal", [resource.values.name])
}

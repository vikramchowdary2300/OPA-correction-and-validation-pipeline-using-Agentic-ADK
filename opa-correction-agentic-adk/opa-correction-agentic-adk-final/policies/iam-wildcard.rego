package policies

import future.keywords.in

deny contains msg if {
	resource := input.planned_values.root_module.resources[_]
	resource.type == "aws_iam_role"
	
	# Parse the policy JSON
	policy := json.unmarshal(resource.values.assume_role_policy)
	
	# Normalize Statement to a list (it can be a single object or a list)
	statements := as_array(policy.Statement)
	
	some statement in statements
	has_wildcard_principal(statement)
	
	msg = sprintf("IAM role %v contains wildcard principal", [resource.values.name])
}

# Helper to normalize object/list to list
as_array(x) = [x] if { is_object(x) }
as_array(x) = x if { is_array(x) }

# Check for wildcard in Principal
has_wildcard_principal(statement) if {
	statement.Effect == "Allow"
	principal := statement.Principal
	
	# Check for "AWS": "*"
	principal.AWS == "*"
}

has_wildcard_principal(statement) if {
	statement.Effect == "Allow"
	principal := statement.Principal
	
	# Check for "AWS": ["*"]
	is_array(principal.AWS)
	principal.AWS[_] == "*"
}

has_wildcard_principal(statement) if {
	statement.Effect == "Allow"
	principal := statement.Principal
	
	# Check for direct wildcard string (rare but possible in some contexts)
	principal == "*"
}

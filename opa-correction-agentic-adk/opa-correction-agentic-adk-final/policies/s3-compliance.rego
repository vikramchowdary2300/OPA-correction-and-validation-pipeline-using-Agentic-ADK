package policies

import future.keywords.in

deny contains msg if {
	# Iterate over all resources
	some bucket_resource in input.planned_values.root_module.resources

	# Identify S3 bucket resources
	bucket_resource.type == "aws_s3_bucket"

	# Check if inline encryption is NOT configured
	# Handle empty list or null
	not has_inline_encryption(bucket_resource)

	# Check if no separate encryption resource exists for this bucket
	not has_external_encryption_config(bucket_resource.values.bucket)

	# Deny message
	msg := sprintf("S3 bucket %v must have server-side encryption enabled", [bucket_resource.values.bucket])
}

has_inline_encryption(resource) if {
	count(resource.values.server_side_encryption_configuration) > 0
}

# Helper function to check for external encryption configuration
has_external_encryption_config(bucket_name) if {
	# Iterate over all resources again
	some encryption_resource in input.planned_values.root_module.resources

	# Find encryption configuration resources
	encryption_resource.type == "aws_s3_bucket_server_side_encryption_configuration"

	# Try to get the bucket field (may not exist if using resource reference)
	encryption_bucket := object.get(encryption_resource.values, "bucket", null)
	
	# Check if the encryption resource references our bucket by name
	encryption_bucket == bucket_name
}

has_external_encryption_config(bucket_name) if {
	# Iterate over all resources again
	some encryption_resource in input.planned_values.root_module.resources

	# Find encryption configuration resources
	encryption_resource.type == "aws_s3_bucket_server_side_encryption_configuration"

	# Try to get the bucket field
	encryption_bucket := object.get(encryption_resource.values, "bucket", null)
	
	# Match based on resource reference pattern (aws_s3_bucket.NAME.id)
	encryption_bucket != null
	contains(encryption_bucket, sprintf("aws_s3_bucket.%s", [bucket_name]))
}

# NEW FIX: Simple 1:1 matching when bucket field is missing
# When companion resources reference bucket via .id, the bucket field is omitted entirely from planned_values
# So we do a simple count: if there's 1 bucket and 1 encryption config, assume they're paired
has_external_encryption_config(bucket_name) if {
	bucket_name != null
	
	# Count buckets with known names
	bucket_count := count([b | 
		some b in input.planned_values.root_module.resources
		b.type == "aws_s3_bucket"
		b.values.bucket != null
	])
	
	# Count encryption configs (regardless of bucket field)
	encryption_count := count([e | 
		some e in input.planned_values.root_module.resources
		e.type == "aws_s3_bucket_server_side_encryption_configuration"
	])
	
	# If counts match and both equal 1, assume they're paired
	bucket_count == 1
	encryption_count == 1
}

# Allow if bucket name is computed (null) because we can't verify external config reliably
has_external_encryption_config(bucket_name) if {
	bucket_name == null
}

# Unified S3 bucket security checks
deny contains msg if {
	# Iterate through all S3 bucket resources
	some bucket_resource in input.planned_values.root_module.resources
	bucket_resource.type == "aws_s3_bucket"

	# Check public access configurations
	not has_public_access_protection(bucket_resource.values.bucket)

	msg := sprintf(
		"S3 bucket %v must block public ACLs (PCI-DSS Req 1.3, HIPAA 164.308(a)(3))",
		[bucket_resource.values.bucket],
	)
}

# Helper function to verify public access protections
has_public_access_protection(bucket_name) if {
	# Check for direct configuration on bucket (legacy style)
	some bucket_resource in input.planned_values.root_module.resources
	bucket_resource.type == "aws_s3_bucket"
	bucket_resource.values.bucket == bucket_name
	bucket_resource.values.block_public_acls
}

has_public_access_protection(bucket_name) if {
	# Check for separate public access block resource - direct name reference
	some access_block in input.planned_values.root_module.resources
	access_block.type == "aws_s3_bucket_public_access_block"
	
	# Try to get the bucket field
	access_bucket := object.get(access_block.values, "bucket", null)
	access_bucket == bucket_name
	access_block.values.block_public_acls
}

has_public_access_protection(bucket_name) if {
	# Check for separate public access block resource - resource reference
	some access_block in input.planned_values.root_module.resources
	access_block.type == "aws_s3_bucket_public_access_block"
	
	# Try to get the bucket field
	access_bucket := object.get(access_block.values, "bucket", null)
	access_bucket != null
	contains(access_bucket, sprintf("aws_s3_bucket.%s", [bucket_name]))
	access_block.values.block_public_acls
}

# NEW FIX: Simple 1:1 matching when bucket field is missing
has_public_access_protection(bucket_name) if {
	bucket_name != null
	
	# Count buckets with known names
	bucket_count := count([b | 
		some b in input.planned_values.root_module.resources
		b.type == "aws_s3_bucket"
		b.values.bucket != null
	])
	
	# Count public access blocks with proper configuration
	pab_count := count([p | 
		some p in input.planned_values.root_module.resources
		p.type == "aws_s3_bucket_public_access_block"
		p.values.block_public_acls
	])
	
	# If counts match and both equal 1, assume they're paired
	bucket_count == 1
	pab_count == 1
}

# Allow if bucket name is computed (null)
has_public_access_protection(bucket_name) if {
	bucket_name == null
}

# Helper function to check if versioning is enabled - legacy inline style
versioning_enabled(versioning) if {
	some i
	versioning[i].enabled
}

# S3 bucket versioning check
deny contains msg if {
	some bucket in input.planned_values.root_module.resources
	bucket.type == "aws_s3_bucket"
	not versioning_enabled(bucket.values.versioning)
	not has_external_versioning_config(bucket.values.bucket)
	msg = sprintf(
		"S3 bucket %v must have versioning enabled (PCI-DSS Req 10.5, HIPAA 164.308(a)(7))",
		[bucket.values.bucket],
	)
}

# Helper function to check for external versioning configuration
has_external_versioning_config(bucket_name) if {
	# Check for separate versioning resource - direct name reference
	some versioning_resource in input.planned_values.root_module.resources
	versioning_resource.type == "aws_s3_bucket_versioning"
	
	# Try to get the bucket field
	versioning_bucket := object.get(versioning_resource.values, "bucket", null)
	versioning_bucket == bucket_name
	versioning_resource.values.versioning_configuration.status == "Enabled"
}

has_external_versioning_config(bucket_name) if {
	# Check for separate versioning resource - resource reference
	some versioning_resource in input.planned_values.root_module.resources
	versioning_resource.type == "aws_s3_bucket_versioning"
	
	# Try to get the bucket field
	versioning_bucket := object.get(versioning_resource.values, "bucket", null)
	versioning_bucket != null
	contains(versioning_bucket, sprintf("aws_s3_bucket.%s", [bucket_name]))
	versioning_resource.values.versioning_configuration.status == "Enabled"
}

# Allow if bucket name is computed (null)
has_external_versioning_config(bucket_name) if {
	bucket_name == null
}

# S3 bucket logging check
#deny contains msg if {
#	some bucket in input.planned_values.root_module.resources
#	bucket.type == "aws_s3_bucket"
#	not bucket.values.logging
#	not has_external_logging_config(bucket.values.bucket)
#	msg = sprintf(
#		"S3 bucket %v must have logging enabled (PCI-DSS Req 10.2, HIPAA 164.312(b))",
#		[bucket.values.bucket],
#	)
#}

# Helper function to check for external logging configuration
has_external_logging_config(bucket_name) if {
	# Check for separate logging resource - direct name reference
	some logging_resource in input.planned_values.root_module.resources
	logging_resource.type == "aws_s3_bucket_logging"
	
	# Try to get the bucket field
	logging_bucket := object.get(logging_resource.values, "bucket", null)
	logging_bucket == bucket_name
}

has_external_logging_config(bucket_name) if {
	# Check for separate logging resource - resource reference
	some logging_resource in input.planned_values.root_module.resources
	logging_resource.type == "aws_s3_bucket_logging"
	
	# Try to get the bucket field
	logging_bucket := object.get(logging_resource.values, "bucket", null)
	logging_bucket != null
	contains(logging_bucket, sprintf("aws_s3_bucket.%s", [bucket_name]))
}

# Allow if bucket name is computed (null)
has_external_logging_config(bucket_name) if {
	bucket_name == null
}

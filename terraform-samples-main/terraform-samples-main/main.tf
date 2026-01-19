# Configure the AWS provider
provider "aws" {
  region = "us-east-1"
} 

# Enable AWS Config for compliance monitoring
resource "aws_config_configuration_recorder" "config" {
  name     = "config-recorder"
  role_arn = aws_iam_role.config_role.arn
  
  recording_group {
    all_supported = true
    include_global_resource_types = true
  }
}

resource "aws_config_delivery_channel" "config" {
  name           = "config-delivery-channel"
  s3_bucket_name = aws_s3_bucket.config_logs.id
  depends_on     = [aws_config_configuration_recorder.config]
}

resource "aws_config_configuration_recorder_status" "config" {
  name       = aws_config_configuration_recorder.config.name
  is_enabled = true
  depends_on = [aws_config_delivery_channel.config]
}

resource "aws_iam_role" "config_role" {
  name = "aws-config-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "config.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "config" {
  role       = aws_iam_role.config_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWS-ConfigRole"
}

resource "aws_s3_bucket" "config_logs" {
  bucket = "aws-config-logs-12345"
}

# Block public access for config logs bucket
resource "aws_s3_bucket_public_access_block" "config_logs" {
  bucket = aws_s3_bucket.config_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable server-side encryption for config logs bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "config_logs" {
  bucket = aws_s3_bucket.config_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Enable logging for config logs bucket
resource "aws_s3_bucket_logging" "config_logs" {
  bucket = aws_s3_bucket.config_logs.id

  target_bucket = aws_s3_bucket.access_logs.id
  target_prefix = "config-logs/"
}

# Enable CloudTrail for the account
resource "aws_cloudtrail" "main" {
  name                          = "main-trail"
  s3_bucket_name                = aws_s3_bucket.cloudtrail_logs.id
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_logging                = true
  enable_log_file_validation    = true
}

resource "aws_s3_bucket" "cloudtrail_logs" {
  bucket = "cloudtrail-logs-12345"
}

# Block public access for CloudTrail logs bucket
resource "aws_s3_bucket_public_access_block" "cloudtrail_logs" {
  bucket = aws_s3_bucket.cloudtrail_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable server-side encryption for CloudTrail logs bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "cloudtrail_logs" {
  bucket = aws_s3_bucket.cloudtrail_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Enable logging for CloudTrail logs bucket
resource "aws_s3_bucket_logging" "cloudtrail_logs" {
  bucket = aws_s3_bucket.cloudtrail_logs.id

  target_bucket = aws_s3_bucket.access_logs.id
  target_prefix = "cloudtrail-logs/"
}

resource "aws_s3_bucket_policy" "cloudtrail_logs" {
  bucket = aws_s3_bucket.cloudtrail_logs.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AWSCloudTrailAclCheck"
        Effect    = "Allow"
        Principal = {"Service": "cloudtrail.amazonaws.com"}
        Action    = "s3:GetBucketAcl"
        Resource  = "arn:aws:s3:::cloudtrail-logs-12345"
      },
      {
        Sid       = "AWSCloudTrailWrite"
        Effect    = "Allow"
        Principal = {"Service": "cloudtrail.amazonaws.com"}
        Action    = "s3:PutObject"
        Resource  = "arn:aws:s3:::cloudtrail-logs-12345/AWSLogs/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }
        }
      }
    ]
  })
}


# Create an S3 bucket
resource "aws_s3_bucket" "my_bucket" {
  bucket = "my-unique-bucket-name-12345"
}

# Create central access logs bucket
resource "aws_s3_bucket" "access_logs" {
  bucket = "central-access-logs-12345"
}

# Block public access for central access logs bucket
resource "aws_s3_bucket_public_access_block" "access_logs" {
  bucket = aws_s3_bucket.access_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable server-side encryption for central access logs bucket
resource "aws_s3_bucket_server_side_encryption_configuration" "access_logs" {
  bucket = aws_s3_bucket.access_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Configure bucket encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "my_bucket" {
  bucket = aws_s3_bucket.my_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block public access
resource "aws_s3_bucket_public_access_block" "my_bucket" {
  bucket = aws_s3_bucket.my_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable S3 bucket logging
resource "aws_s3_bucket_logging" "my_bucket" {
  bucket = aws_s3_bucket.my_bucket.id

  target_bucket = aws_s3_bucket.log_bucket.id
  target_prefix = "log/"
}

# Create logging bucket for S3 access logs
resource "aws_s3_bucket" "log_bucket" {
  bucket = "my-unique-bucket-logs-12345"
}

# Block public access for my bucket logs
resource "aws_s3_bucket_public_access_block" "log_bucket" {
  bucket = aws_s3_bucket.log_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable server-side encryption for my bucket logs
resource "aws_s3_bucket_server_side_encryption_configuration" "log_bucket" {
  bucket = aws_s3_bucket.log_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Enable logging for log bucket
resource "aws_s3_bucket_logging" "log_bucket" {
  bucket = aws_s3_bucket.log_bucket.id

  target_bucket = aws_s3_bucket.access_logs.id
  target_prefix = "log-bucket/"
}

# Create an EC2 instance
resource "aws_instance" "my_instance" {
  ami           = "ami-0c55b159cbfafe1f0"  # Example AMI ID for Amazon Linux 2 in us-east-1, change it based on your region
  instance_type = "t2.micro"
  key_name      = "my-key-pair"  # Ensure you have created a key pair in your AWS account for SSH access

  tags = {
    Name = "MyEC2Instance"
  }
}

# Outputs for reference
output "s3_bucket_name" {
  value = aws_s3_bucket.my_bucket.bucket
}

output "ec2_instance_id" {
  value = aws_instance.my_instance.id
}

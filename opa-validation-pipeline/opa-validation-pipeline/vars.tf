variable "owner" {
  default     = "@student.ncirl.ie"
  description = "Used for tagging of the instance. Important for billing and cost analysis. e.g. john.smith@workhuman.com"
  type        = string
}

variable "team" {
  default     = "NCI-Cloud-Computing"
  description = "The string to use for the course tag that will be applied to all created resources."
  type        = string
}

variable "region" {
  description = "The AWS region."
  type        = string
  default     = "eu-west-1"
}

variable "environment" {
  description = "The AWS environment."
  type        = string
}

variable "app_repo" {
  description = "The path to the repo of the app code (leave off the workhuman prefix)."
  type        = string
  default     = "workhuman/ecommerce-store/recommendations/recommendations-app"
}

variable "ecs_buildspec" {
  default     = "buildspec-ecs.yml"
  description = "The name of the buildspec file in the ecs-src-repo. When unset, CodeBuild looks for a file named buildspec.yml"
  type        = string
}

variable "ecs_codebuild_image" {
  default     = "aws/codebuild/amazonlinux2-aarch64-standard:3.0"
  description = "CodeBuild Image to use https://docs.aws.amazon.com/codebuild/latest/userguide/available-runtimes.html"
  type        = string
}

variable "ecs_task_cpu" {
  default     = 256
  description = "The CPU allocated to the ECS task. Ref: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/fargate-tasks-services.html#fargate-tasks-size"
  type        = number
}

variable "ecs_task_memory" {
  default     = 512
  description = "The memory allocated to the ECS task. Ref: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/fargate-tasks-services.html#fargate-tasks-size"
  type        = number
}

variable "health_check_path" {
  default     = "/actuator/health"
  description = "The path the ALB will use for health checking your service."
  type        = string
}

variable "health_check_port" {
  default     = 8080
  description = "The port the ALB will use for health checking your service."
  type        = number
}

variable "ecr_src_tag" {
  default     = "latest"
  description = "The Docker tag used for the event bridge rule."
  type        = string
}

variable "ecs_src_branch" {
  default     = "master"
  description = "The name of the zip file for the source of the ECS pipeline code."
  type        = string
}

# This should not be enabled when using Gitlab pipelines
variable "set_pipeline_ecr_event" {
  default     = false
  description = "Set a cloudwatch event to trigger deployment when pushes are detected on the target ecr for the ecr_src_tag tag"
  type        = bool
}

# This should not be enabled when using Gitlab pipelines
variable "set_pipeline_ecs_event" {
  default     = false
  description = "Set a cloudwatch event to trigger deployment when pushes are detected on the target taskdef S3"
  type        = bool
}

variable "iam_resource_name_extra_str" {
  default     = ""
  description = "String to add to iam resource names"
  type        = string
}

variable "ecs_schedule_enabled" {
  default     = true
  description = "Enable scheduling for the ECS autoscaling."
  type        = bool
}

variable "ecs_schedule_scale_down" {
  default     = "cron(0 18 * * ? *)"
  description = "Scaling down daily at 6pm UTC / 7pm Dublin / 9pm Belarus / 2pm Boston"
  type        = string
}

variable "ecs_schedule_scale_up" {
  description = "Scaling up daily at 5am UTC / 6am Dublin / 8am Belarus / 1am Boston"
  type        = string
  default     = "cron(0 5 * * ? *)"
}


variable "ecs_autoscaling_max_capacity" {
  default     = null
  description = "The max capacity of the scalable target."
  type        = number
}

variable "ecs_autoscaling_max_capacity_down" {
  default     = 1
  description = "The max capacity of the scalable target for when it's scheduled down."
  type        = number
}

variable "ecs_autoscaling_min_capacity" {
  default     = 1
  description = "The min capacity of the scalable target."
  type        = number
}

variable "ecs_autoscaling_scale_in_cooldown" {
  default     = 300
  description = "The amount of time, in seconds, after a scale in activity completes before another scale in activity can start."
  type        = number
}

variable "ecs_autoscaling_scale_out_cooldown" {
  default     = 300
  description = "The amount of time, in seconds, after a scale out activity completes before another scale out activity can start."
  type        = number
}

variable "ecs_autoscaling_target_value" {
  default     = 50
  description = "The target value for the metric."
  type        = number
}

variable "ecs_cpu_high_alarm_threshold" {
  default     = 50
  description = "The CPU threshold to alarm at."
  type        = number
}

variable "ecs_mem_high_alarm_threshold" {
  default     = 80
  description = "The Memory threshold to alarm at."
  type        = string
}

variable "tf_branch" {
  # calculated on-fly in scope of terraform apply
  description = "The Git branch being applied."
  type        = string
}

variable "repository_name" {
  # calculated on-fly in scope of terraform apply
  description = "The path to the Git repository (under the terraform group) being applied."
  type        = string
}

variable "aws_secret_key" {
  description = "The path to the Git repository (under the terraform group) being applied."
  type        = string
}

variable "aws_access_key" {
  description = "The path to the Git repository (under the terraform group) being applied."
  type        = string
}

variable "application_name" {
  description = "The string to use for the Application tag that will be applied to all created resources."
  type        = string
}

variable "github_homepage_url" {
  description = "NCI Application Name"
  type        = string
}

variable "github_security_token" {
  description = "NCI Application Name"
  type        = string
}

variable "github_username" {
  description = "NCI Application Name"
  type        = string
}


variable "email_id" {
  description = "Email ID for Notification"
  type        = string
}


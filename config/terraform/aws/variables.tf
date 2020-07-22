###
# Global
###
variable "region" {
  type = string
}

variable "billing_tag_key" {
  type = string
}

variable "billing_tag_value" {
  type = string
}

###
# AWS Cloud Watch - cloudwatch.tf
###
variable "cloudwatch_log_group_name" {
  type = string
}

###
# AWS ECS - ecs.tf
###
variable "github_sha" {
  type    = string
  default = ""
}

variable "ecs_name" {
  type = string
}

variable "scale_in_cooldown" {
  type    = number
  default = 60
}
variable "scale_out_cooldown" {
  type    = number
  default = 60
}
variable "cpu_scale_metric" {
  type    = number
  default = 60
}
variable "memory_scale_metric" {
  type    = number
  default = 60
}
variable "min_capacity" {
  type    = number
  default = 2
}
variable "max_capacity" {
  type    = number
  default = 10
}

# Task Covid Portal
variable "ecs_covid_portal_name" {
  type = string
}

variable "ecs_task_env_api_authorization"{
  type = string
}

variable "ecs_task_env_api_endpoint"{
  type = string
}

variable "ecs_task_env_default_from_email"{
  type = string
}

variable "ecs_task_env_django_admins"{
  type = string
}

variable "ecs_task_env_django_secret_key"{
  type = string
}

variable "ecs_task_env_email_host"{
  type = string
}

variable "ecs_task_env_email_host_user"{
  type = string
}

variable "ecs_task_env_email_host_password"{
  type = string
}

variable "ecs_task_env_email_port"{
  type = string
  default = "587"
}

variable "ecs_task_env_email_use_tls"{
  type = string
  default = "True"
}

variable "ecs_task_env_new_relic_license_key"{
  type = string
}

variable "django_env"{
  type = string
  default = "production"
}

variable "django_allowed_hosts"{
  type = string
}

variable "email_backend"{
  type = string
  default = "'django.core.mail.backends.smtp.EmailBackend'"
}

variable "new_relic_app_name"{
  type = string
}




# Covid Portal Scaling 

variable "portal_autoscale_enabled" {
  type = bool
}

variable "manual_deploy_enabled" {
  type    = bool
  default = false
}

variable "termination_wait_time_in_minutes" {
  type        = number
  description = "minutes to wait to terminate old deploy"
  default     = 1
}

# Metric provider
variable "metric_provider" {
  type = string
}

# Tracing provider
variable "tracer_provider" {
  type = string
}

###
# AWS VPC - networking.tf
###
variable "vpc_cidr_block" {
  type = string
}

variable "vpc_name" {
  type = string
}

###
# AWS RDS - rds.tf
###
# RDS Subnet Group
variable "rds_db_subnet_group_name" {
  type = string
}

# RDS DB - Key Retrieval/Submission
variable "rds_server_db_name" {
  type = string
}

variable "rds_server_name"{
  type = string
}

variable "rds_server_db_user" {
  type = string
}

variable "rds_server_db_password" {
  type = string
}

variable "rds_server_allocated_storage" {
  type = string
}

variable "rds_server_instance_class" {
  type = string
}

###
# AWS Route53 - route53.tf
###
variable "route53_zone_name" {
  type = string
}

###
# AWS WAF - IPs/CIDRs to allow to /new-key-claim
###
variable "new_key_claim_allow_list" {
  type    = list
  default = ["0.0.0.0/1", "128.0.0.0/1"]
}

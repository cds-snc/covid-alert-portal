###
# Global
###

region = "ca-central-1"
# Enable the new ARN format to propagate tags to containers (see config/terraform/aws/README.md)
billing_tag_key   = "CostCentre"
billing_tag_value = "CovidPortal_dev"

###
# AWS Cloud Watch - cloudwatch.tf
###

cloudwatch_log_group_name        = "covidportal_dev"
cloudwatch_log_group_name_qrcode = "qrcode_dev"

###
# AWS ECS - ecs.tf
###

ecs_name              = "covid-portal_dev"
metric_provider       = "stdout"
tracer_provider       = "stdout"
django_env            = "production"
django_allowed_hosts  = ".cdssandbox.xyz"
ecs_covid_portal_name = "covid-portal_dev"
ecs_qrcode_name       = "qrcode_dev"
new_relic_app_name    = "Dev-Terraform-Covid-Portal"
dual_urls             = "False"


#Autoscaling ECS

portal_autoscale_enabled = false

###
# AWS VPC - networking.tf
###

vpc_cidr_block = "172.16.0.0/16"
vpc_name       = "covidportal"

###
# AWS RDS - rds.tf
###

rds_db_subnet_group_name = "dev-portal-db"

# RDS Cluster
rds_server_db_name = "covid_portal"
rds_server_name    = "dev-covidportal-db"
rds_server_db_user = "postgres"
# Value should come from a TF_VAR environment variable (e.g. set in a Github Secret)
rds_server_db_password       = "Kingoftheworld!"
rds_server_allocated_storage = "5"
rds_server_instance_class    = "db.t3.medium"

###
# AWS Route 53 - route53.tf
###
# Value should come from a TF_VAR environment variable (e.g. set in a Github Secret)
route53_zone_name = "dev.covid-hcportal.cdssandbox.xyz"

###
# Local development environment
###
slack_webhook                                     = ""
ecs_secret_api_authorization                      = ""
ecs_secret_api_endpoint                           = "https://submission.wild-samphire.cdssandbox.xyz/new-key-claim"
ecs_secret_django_secret_key                      = "secret_key_goes_here"
ecs_secret_notify_api_key                         = ""
ecs_secret_notify_template_id                     = "eac546b3-90c3-4834-82fb-7fb9be564c81"
ecs_secret_otk_sms_template_id_en                 = "40864010-5323-49e9-9828-3ae8e376535c"
ecs_secret_otk_sms_template_id_fr                 = "1ccf1412-b84e-4e3d-a7a9-6555b0f5b727"
ecs_secret_backup_code_admin_email_template_id_en = "158a633d-da11-4a6f-acf3-9797adf0d1ae"
ecs_secret_backup_code_admin_email_template_id_fr = "e3bf4a89-eec2-4af6-ac1a-1145cc8a211c"
ecs_secret_password_reset_email_template_id_fr    = "8ab7edfe-aaf5-4e78-80a6-0d72e7e0ad3b"
ecs_secret_password_reset_email_template_id_en    = "610b49ce-ed71-42df-a003-53c9abdf7368"
ecs_secret_invitation_email_template_id_en        = "6407660d-1747-4c01-896d-da25566402e0"
ecs_secret_invitation_email_template_id_fr        = "83ee8ec9-93e8-4cca-8c6a-3eeb174bfbd9"
ecs_secret_confirmation_email_template_id_en      = "bdbb9cb0-2e44-41c1-9aed-58507ec92fef"
ecs_secret_confirmation_email_template_id_fr      = "4d9c284d-fedf-46a7-8ca1-0133bc98ca6e"

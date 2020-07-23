resource "aws_secretsmanager_secret" "server_database_url" {
  name = "server-database-url"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "server_database_url" {
  secret_id     = aws_secretsmanager_secret.server_database_url.id
  secret_string = "postgres://${var.rds_server_db_user}:${var.rds_server_db_password}@${aws_rds_cluster.covidportal_server.endpoint}:5432/${var.rds_server_db_name}"
}

###
# AWS Secret Manager - Covid Alert Portal
###

resource "aws_secretsmanager_secret" "env_api_authorization"{
  name = "env_api_authorization"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "env_api_authorization"{
  secret_id = aws_secretsmanager_secret.env_api_authorization.id 
  secret_string = var.ecs_task_env_api_authorization
}

resource "aws_secretsmanager_secret" "env_api_endpoint"{
  name = "env_api_endpoint"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "env_api_endpoint"{
  secret_id = aws_secretsmanager_secret.env_api_endpoint.id 
  secret_string = var.ecs_task_env_api_endpoint
}

resource "aws_secretsmanager_secret" "env_default_from_email"{
  name = "env_default_from_email"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "env_default_from_email"{
  secret_id = aws_secretsmanager_secret.env_default_from_email.id 
  secret_string = var.ecs_task_env_default_from_email
}

resource "aws_secretsmanager_secret" "env_django_admins"{
  name = "env_django_admins"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "env_django_admins"{
  secret_id = aws_secretsmanager_secret.env_django_admins.id 
  secret_string = var.ecs_task_env_django_admins
}

resource "aws_secretsmanager_secret" "env_django_secret_key"{
  name = "env_django_secret_key"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "env_django_secret_key"{
  secret_id = aws_secretsmanager_secret.env_django_secret_key.id 
  secret_string = var.ecs_task_env_django_secret_key
}

resource "aws_secretsmanager_secret" "env_email_host"{
  name = "env_email_host"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "env_email_host"{
  secret_id = aws_secretsmanager_secret.env_email_host.id 
  secret_string = var.ecs_task_env_email_host
}

resource "aws_secretsmanager_secret" "env_email_host_user"{
  name = "env_email_host_use"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "env_email_host_user"{
  secret_id = aws_secretsmanager_secret.env_email_host_user.id 
  secret_string = var.ecs_task_env_email_host_user
}

resource "aws_secretsmanager_secret" "env_email_host_password"{
  name = "env_email_host_password"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "env_email_host_password"{
  secret_id = aws_secretsmanager_secret.env_email_host_password.id 
  secret_string = var.ecs_task_env_email_host_password
}

resource "aws_secretsmanager_secret" "env_email_port"{
  name = "env_email_port"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "env_email_port"{
  secret_id = aws_secretsmanager_secret.env_email_port.id 
  secret_string = var.ecs_task_env_email_port #tfsec:ignore:GEN003
}

resource "aws_secretsmanager_secret" "env_email_use_tls"{
  name = "env_email_use_tls"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "env_email_use_tls"{
  secret_id = aws_secretsmanager_secret.env_email_use_tls.id 
  secret_string = var.ecs_task_env_email_use_tls #tfsec:ignore:GEN003
}

resource "aws_secretsmanager_secret" "env_new_relic_license_key"{
  name = "env_new_relic_license_key"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "env_new_relic_license_key"{
  secret_id = aws_secretsmanager_secret.env_new_relic_license_key.id 
  secret_string = var.ecs_task_env_new_relic_license_key
}

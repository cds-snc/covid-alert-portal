resource "aws_secretsmanager_secret" "server_database_url" {
  name                    = "server-database-url"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "server_database_url" {
  secret_id     = aws_secretsmanager_secret.server_database_url.id
  secret_string = "postgres://${var.rds_server_db_user}:${var.rds_server_db_password}@${aws_rds_cluster.covidportal_server.endpoint}:5432/${var.rds_server_db_name}"
}

###
# AWS Secret Manager - Covid Alert Portal
###

resource "aws_secretsmanager_secret" "api_authorization" {
  name                    = "api_authorization"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "api_authorization" {
  secret_id     = aws_secretsmanager_secret.api_authorization.id
  secret_string = var.ecs_secret_api_authorization
}

resource "aws_secretsmanager_secret" "api_endpoint" {
  name                    = "api_endpoint"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "api_endpoint" {
  secret_id     = aws_secretsmanager_secret.api_endpoint.id
  secret_string = var.ecs_secret_api_endpoint
}

resource "aws_secretsmanager_secret" "django_secret_key" {
  name                    = "django_secret_key"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "django_secret_key" {
  secret_id     = aws_secretsmanager_secret.django_secret_key.id
  secret_string = var.ecs_secret_django_secret_key
}

resource "aws_secretsmanager_secret" "freshdesk_api_endpoint" {
  name                    = "freshdesk_api_endpoint"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "freshdesk_api_endpoint" {
  secret_id     = aws_secretsmanager_secret.freshdesk_api_endpoint.id
  secret_string = var.ecs_secret_freshdesk_api_endpoint
}

resource "aws_secretsmanager_secret" "freshdesk_api_key" {
  name                    = "freshdesk_api_key"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "freshdesk_api_key" {
  secret_id     = aws_secretsmanager_secret.freshdesk_api_key.id
  secret_string = var.ecs_secret_freshdesk_api_key
}

resource "aws_secretsmanager_secret" "freshdesk_product_id" {
  name                    = "freshdesk_product_id"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "freshdesk_product_id" {
  secret_id     = aws_secretsmanager_secret.freshdesk_product_id.id
  secret_string = var.ecs_secret_freshdesk_product_id
}

resource "aws_secretsmanager_secret" "new_relic_license_key" {
  name                    = "new_relic_license_key"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "new_relic_license_key" {
  secret_id     = aws_secretsmanager_secret.new_relic_license_key.id
  secret_string = var.ecs_secret_new_relic_license_key
}

resource "aws_secretsmanager_secret" "notify_api_key" {
  name                    = "notify_api_key"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "notify_api_key" {
  secret_id     = aws_secretsmanager_secret.notify_api_key.id
  secret_string = var.ecs_secret_notify_api_key
}

resource "aws_secretsmanager_secret" "qrcode_signature_private_key" {
  name                    = "qrcode_signature_private_key"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "qrcode_signature_private_key" {
  secret_id     = aws_secretsmanager_secret.qrcode_signature_private_key.id
  secret_string = var.ecs_secret_qrcode_signature_private_key
}
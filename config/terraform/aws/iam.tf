data "aws_iam_policy_document" "covidportal" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

###
# AWS IAM - Covid Alert Portal
###

data "aws_iam_policy_document" "covidportal_secrets_manager" {
  statement {
    effect = "Allow"

    actions = [
      "secretsmanager:GetSecretValue",
    ]

    resources = [
      aws_secretsmanager_secret.server_database_url.arn,
      aws_secretsmanager_secret_version.env_api_authorization.arn,
      aws_secretsmanager_secret_version.env_api_endpoint.arn,
      aws_secretsmanager_secret_version.env_default_from_email.arn,
      aws_secretsmanager_secret_version.env_django_admins.arn,
      aws_secretsmanager_secret_version.env_django_secret_key.arn,
      aws_secretsmanager_secret_version.env_email_host.arn,
      aws_secretsmanager_secret_version.env_email_host_user.arn,
      aws_secretsmanager_secret_version.env_email_host_password.arn,
      aws_secretsmanager_secret_version.env_email_port.arn,
      aws_secretsmanager_secret_version.env_email_use_tls.arn,
      aws_secretsmanager_secret_version.env_new_relic_license_key.arn,
    ]
  }
}

resource "aws_iam_policy" "covidportal_secrets_manager" {
  name   = "covidportalSecretsManagerKeyRetrieval"
  path   = "/"
  policy = data.aws_iam_policy_document.covidportal_secrets_manager.json
}

resource "aws_iam_role" "covidportal" {
  name = var.ecs_covid_portal_name

  assume_role_policy = data.aws_iam_policy_document.covidportal.json

  tags = {
    (var.billing_tag_key) = var.billing_tag_value
  }
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_covid_portal" {
  role       = aws_iam_role.covidportal.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "secrets_manager_covid_portal" {
  role       = aws_iam_role.covidportal.name
  policy_arn = aws_iam_policy.covidportal_secrets_manager.arn
}

###
# AWS IAM - Codedeploy
###

resource "aws_iam_role" "codedeploy" {
  name               = "codedeploy"
  assume_role_policy = data.aws_iam_policy_document.assume_role_policy_codedeploy.json
  path               = "/"
}

data "aws_iam_policy_document" "assume_role_policy_codedeploy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["codedeploy.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "codedeploy" {
  role       = aws_iam_role.codedeploy.name
  policy_arn = "arn:aws:iam::aws:policy/AWSCodeDeployRoleForECS"
}

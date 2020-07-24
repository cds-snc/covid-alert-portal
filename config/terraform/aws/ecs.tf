###
# ECS Cluster
###

resource "aws_ecs_cluster" "covidportal" {
  name = var.ecs_name

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    (var.billing_tag_key) = var.billing_tag_value
  }
}

locals {
  portal_repo  = aws_ecr_repository.repository.repository_url
}

###
# ECS - Covid Portal
###

# Task Definition

data "template_file" "covidportal_task" {
  template = file("task-definitions/covid-portal.json")

  vars = {
    image                 = "${local.portal_repo}"
    awslogs-group         = aws_cloudwatch_log_group.covidportal.name
    awslogs-region        = var.region
    awslogs-stream-prefix = "ecs-${var.ecs_covid_portal_name}"
    database_url          = aws_secretsmanager_secret_version.server_database_url.arn
    metric_provider       = var.metric_provider
    tracer_provider       = var.tracer_provider
    api_authorization     = aws_secretsmanager_secret_version.env_api_authorization.arn
    api_endpoint          = aws_secretsmanager_secret_version.env_api_endpoint.arn
    default_from_email    = aws_secretsmanager_secret_version.env_default_from_email.arn
    django_admins         = aws_secretsmanager_secret_version.env_django_admins.arn
    django_secret_key     = aws_secretsmanager_secret_version.env_django_secret_key.arn
    email_host            = aws_secretsmanager_secret_version.env_email_host.arn
    email_host_user       = aws_secretsmanager_secret_version.env_email_host_user.arn
    email_host_password   = aws_secretsmanager_secret_version.env_email_host_password.arn
    email_port            = aws_secretsmanager_secret_version.env_email_port.arn
    email_use_tls         = aws_secretsmanager_secret_version.env_email_use_tls.arn
    new_relic_license_key = aws_secretsmanager_secret_version.env_new_relic_license_key.arn
    django_env            = var.django_env
    django_allowed_hosts  = var.django_allowed_hosts
    django_email_backend  = var.email_backend
    new_relic_app_name    = var.new_relic_app_name

  }
}

resource "aws_ecs_task_definition" "covidportal" {
  family       = var.ecs_covid_portal_name
  cpu          = 2048
  memory       = "4096"
  network_mode = "awsvpc"

  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.covidportal.arn
  task_role_arn            = aws_iam_role.covidportal.arn
  container_definitions    = data.template_file.covidportal_task.rendered

  tags = {
    (var.billing_tag_key) = var.billing_tag_value
  }
}

# Service

resource "aws_ecs_service" "covidportal" {
  depends_on = [
    aws_lb_listener.covidportal_https,
    aws_lb_listener.covidportal_http
  ]

  name             = var.ecs_covid_portal_name
  cluster          = aws_ecs_cluster.covidportal.id
  task_definition  = aws_ecs_task_definition.covidportal.arn
  launch_type      = "FARGATE"
  platform_version = "1.4.0"
  # Enable the new ARN format to propagate tags to containers (see config/terraform/aws/README.md)
  propagate_tags = "SERVICE"

  desired_count                      = 2
  deployment_minimum_healthy_percent = 50
  deployment_maximum_percent         = 200
  health_check_grace_period_seconds  = 60
  deployment_controller {
    type = "CODE_DEPLOY"
  }

  network_configuration {
    assign_public_ip = false
    subnets          = aws_subnet.covidportal_private.*.id
    security_groups = [
      aws_security_group.covidportal.id,
      aws_security_group.covidportal_egress.id
    ]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.covidportal.arn
    container_name   = "covid-portal"
    container_port   = 8000
  }

  tags = {
    (var.billing_tag_key) = var.billing_tag_value
  }

  lifecycle {
    ignore_changes = [
      desired_count,   # updated by autoscaling
      task_definition, # updated by codedeploy
      load_balancer    # updated by codedeploy
    ]
  }

}

resource "aws_appautoscaling_target" "portal" {
  count              = var.portal_autoscale_enabled ? 1 : 0
  service_namespace  = "ecs"
  resource_id        = "service/${aws_ecs_service.covidportal.cluster}/${aws_ecs_service.covidportal.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  min_capacity       = var.min_capacity
  max_capacity       = var.max_capacity
}
resource "aws_appautoscaling_policy" "portal_cpu" {
  count              = var.portal_autoscale_enabled ? 1 : 0
  name               = "portal_cpu"
  policy_type        = "TargetTrackingScaling"
  service_namespace  = "ecs"
  resource_id        = "service/${aws_ecs_service.covidportal.cluster}/${aws_ecs_service.covidportal.name}"
  scalable_dimension = "ecs:service:DesiredCount"

  target_tracking_scaling_policy_configuration {
    scale_in_cooldown  = var.scale_in_cooldown
    scale_out_cooldown = var.scale_out_cooldown
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = var.cpu_scale_metric
  }
}

resource "aws_appautoscaling_policy" "portal_memory" {
  count              = var.portal_autoscale_enabled ? 1 : 0
  name               = "portal_memory"
  policy_type        = "TargetTrackingScaling"
  service_namespace  = "ecs"
  resource_id        = "service/${aws_ecs_service.covidportal.cluster}/${aws_ecs_service.covidportal.name}"
  scalable_dimension = "ecs:service:DesiredCount"

  target_tracking_scaling_policy_configuration {
    scale_in_cooldown  = var.scale_in_cooldown
    scale_out_cooldown = var.scale_out_cooldown
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    target_value = var.memory_scale_metric
  }
}

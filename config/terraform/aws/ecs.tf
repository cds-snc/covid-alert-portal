###
# ECS Cluster
###

resource "aws_ecs_cluster" "covidportal" {
  name = var.ecs_name

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  capacity_providers = ["FARGATE"]

  default_capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 1
    base              = 2
  }

  tags = {
    (var.billing_tag_key) = var.billing_tag_value
  }
}

locals {
  portal_repo = aws_ecr_repository.repository.repository_url
}

###
# ECS - Covid Portal
###

# Task Definitions

data "template_file" "covidportal_task" {
  template = file("task-definitions/covid-portal.json")

  vars = {
    app_switch                   = "PORTAL"
    name                         = var.ecs_covid_portal_name
    image                        = "${local.portal_repo}"
    awslogs-group                = aws_cloudwatch_log_group.covidportal.name
    awslogs-region               = var.region
    awslogs-stream-prefix        = "ecs-${var.ecs_covid_portal_name}"
    database_url                 = aws_secretsmanager_secret_version.server_database_url.arn
    metric_provider              = var.metric_provider
    tracer_provider              = var.tracer_provider
    api_authorization            = aws_secretsmanager_secret_version.api_authorization.arn
    api_endpoint                 = aws_secretsmanager_secret_version.api_endpoint.arn
    django_secret_key            = aws_secretsmanager_secret_version.django_secret_key.arn
    freshdesk_api_endpoint       = aws_secretsmanager_secret_version.freshdesk_api_endpoint.arn
    freshdesk_api_key            = aws_secretsmanager_secret_version.freshdesk_api_key.arn
    freshdesk_product_id         = aws_secretsmanager_secret_version.freshdesk_product_id.arn
    new_relic_license_key        = aws_secretsmanager_secret_version.new_relic_license_key.arn
    django_env                   = var.django_env
    django_allowed_hosts         = var.django_allowed_hosts
    new_relic_app_name           = var.new_relic_app_name
    dual_urls                    = var.dual_urls
    notify_api_key               = aws_secretsmanager_secret_version.notify_api_key.arn
    qrcode_signature_private_key = aws_secretsmanager_secret_version.qrcode_signature_private_key.arn
    qrcode_notify_api_key        = aws_secretsmanager_secret_version.qrcode_notify_api_key.arn
  }
}

data "template_file" "qrcode_registration_task" {
  template = file("task-definitions/covid-portal.json")

  vars = {
    app_switch                   = "QRCODE"
    name                         = var.ecs_covid_portal_name
    image                        = "${local.portal_repo}"
    awslogs-group                = aws_cloudwatch_log_group.qrcode.name
    awslogs-region               = var.region
    awslogs-stream-prefix        = "ecs-${var.ecs_qrcode_name}"
    database_url                 = aws_secretsmanager_secret_version.server_database_url.arn
    metric_provider              = var.metric_provider
    tracer_provider              = var.tracer_provider
    api_authorization            = aws_secretsmanager_secret_version.api_authorization.arn
    api_endpoint                 = aws_secretsmanager_secret_version.api_endpoint.arn
    django_secret_key            = aws_secretsmanager_secret_version.django_secret_key.arn
    freshdesk_api_endpoint       = aws_secretsmanager_secret_version.freshdesk_api_endpoint.arn
    freshdesk_api_key            = aws_secretsmanager_secret_version.freshdesk_api_key.arn
    freshdesk_product_id         = aws_secretsmanager_secret_version.freshdesk_product_id.arn
    new_relic_license_key        = aws_secretsmanager_secret_version.new_relic_license_key.arn
    django_env                   = var.django_env
    django_allowed_hosts         = var.django_allowed_hosts
    new_relic_app_name           = var.new_relic_app_name
    dual_urls                    = var.dual_urls
    notify_api_key               = aws_secretsmanager_secret_version.notify_api_key.arn
    qrcode_signature_private_key = aws_secretsmanager_secret_version.qrcode_signature_private_key.arn
    qrcode_notify_api_key        = aws_secretsmanager_secret_version.qrcode_notify_api_key.arn
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
resource "aws_ecs_task_definition" "qrcode" {
  family       = var.ecs_qrcode_name
  cpu          = 2048
  memory       = "4096"
  network_mode = "awsvpc"

  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.covidportal.arn
  task_role_arn            = aws_iam_role.covidportal.arn
  container_definitions    = data.template_file.qrcode_registration_task.rendered

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
    container_name   = var.ecs_covid_portal_name
    container_port   = 8000
  }

  capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 1
    base              = 2
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

resource "aws_ecs_service" "qrcode" {
  depends_on = [
    aws_lb_listener.qrcode_https,
    aws_lb_listener.qrcode_http
  ]

  name             = var.ecs_qrcode_name
  cluster          = aws_ecs_cluster.covidportal.id
  task_definition  = aws_ecs_task_definition.qrcode.arn
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
      aws_security_group.qrcode.id,
      aws_security_group.qrcode_egress.id
    ]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.qrcode.arn
    container_name   = var.ecs_covid_portal_name
    container_port   = 8000
  }

  capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 1
    base              = 2
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
  resource_id        = "service/${aws_ecs_cluster.covidportal.name}/${aws_ecs_service.covidportal.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  min_capacity       = var.min_capacity
  max_capacity       = var.max_capacity
}
resource "aws_appautoscaling_policy" "portal_cpu" {
  count              = var.portal_autoscale_enabled ? 1 : 0
  name               = "portal_cpu"
  policy_type        = "TargetTrackingScaling"
  service_namespace  = aws_appautoscaling_target.portal[count.index].service_namespace
  resource_id        = aws_appautoscaling_target.portal[count.index].resource_id
  scalable_dimension = aws_appautoscaling_target.portal[count.index].scalable_dimension

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
  service_namespace  = aws_appautoscaling_target.portal[count.index].service_namespace
  resource_id        = aws_appautoscaling_target.portal[count.index].resource_id
  scalable_dimension = aws_appautoscaling_target.portal[count.index].scalable_dimension

  target_tracking_scaling_policy_configuration {
    scale_in_cooldown  = var.scale_in_cooldown
    scale_out_cooldown = var.scale_out_cooldown
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    target_value = var.memory_scale_metric
  }
}

resource "aws_appautoscaling_target" "qrcode" {
  count              = var.portal_autoscale_enabled ? 1 : 0
  service_namespace  = "ecs"
  resource_id        = "service/${aws_ecs_cluster.covidportal.name}/${aws_ecs_service.qrcode.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  min_capacity       = var.min_capacity
  max_capacity       = var.max_capacity
}
resource "aws_appautoscaling_policy" "qrcode_cpu" {
  count              = var.portal_autoscale_enabled ? 1 : 0
  name               = "qrcode_cpu"
  policy_type        = "TargetTrackingScaling"
  service_namespace  = aws_appautoscaling_target.qrcode[count.index].service_namespace
  resource_id        = aws_appautoscaling_target.qrcode[count.index].resource_id
  scalable_dimension = aws_appautoscaling_target.qrcode[count.index].scalable_dimension

  target_tracking_scaling_policy_configuration {
    scale_in_cooldown  = var.scale_in_cooldown
    scale_out_cooldown = var.scale_out_cooldown
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = var.cpu_scale_metric
  }
}

resource "aws_appautoscaling_policy" "qrcode_memory" {
  count              = var.portal_autoscale_enabled ? 1 : 0
  name               = "portal_memory"
  policy_type        = "TargetTrackingScaling"
  service_namespace  = aws_appautoscaling_target.qrcode[count.index].service_namespace
  resource_id        = aws_appautoscaling_target.qrcode[count.index].resource_id
  scalable_dimension = aws_appautoscaling_target.qrcode[count.index].scalable_dimension

  target_tracking_scaling_policy_configuration {
    scale_in_cooldown  = var.scale_in_cooldown
    scale_out_cooldown = var.scale_out_cooldown
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    target_value = var.memory_scale_metric
  }
}

resource "aws_cloudwatch_log_group" "covidportal" {
  name       = var.cloudwatch_log_group_name
  kms_key_id = aws_kms_key.cw.arn

  tags = {
    (var.billing_tag_key) = var.billing_tag_value
  }
}

###
# AWS CloudWatch Metrics - Scaling metrics
###

resource "aws_cloudwatch_metric_alarm" "portal_cpu_utilization_high" {
  alarm_name          = "portal-cpu-utilization-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "120"
  statistic           = "Average"
  threshold           = "50"
  alarm_description   = "This metric monitors ecs cpu utilization"

  alarm_actions = [aws_sns_topic.alert_warning.arn]
  dimensions = {
    ClusterName = aws_ecs_cluster.covidportal.name
    ServiceName = aws_ecs_service.covidportal.name
  }
}

resource "aws_cloudwatch_metric_alarm" "portal_memory_utilization_high" {
  alarm_name          = "portal-memory-utilization-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = "120"
  statistic           = "Average"
  threshold           = "50"
  alarm_description   = "This metric monitors ecs memory utilization"

  alarm_actions = [aws_sns_topic.alert_warning.arn]

  dimensions = {
    ClusterName = aws_ecs_cluster.covidportal.name
    ServiceName = aws_ecs_service.covidportal.name
  }
}


###
# AWS CloudWatch Metrics - Code errors
###

resource "aws_cloudwatch_log_metric_filter" "five_hundred_response" {
  name           = "500Response"
  pattern        = "statusClass=5xx msg=\"http response\""
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "500Response"
    namespace = "covidportal"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "five_hundred_response_warn" {
  alarm_name          = "500ResponseWarn"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = aws_cloudwatch_log_metric_filter.five_hundred_response.name
  namespace           = "covidportal"
  period              = "60"
  statistic           = "Sum"
  threshold           = "1"
  alarm_description   = "This metric monitors for an 5xx level response"

  alarm_actions = [aws_sns_topic.alert_warning.arn]
}

resource "aws_cloudwatch_log_metric_filter" "error_logged" {
  name           = "ErrorLogged"
  pattern        = "level=error"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "ErrorLogged"
    namespace = "covidportal"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "error_logged_warn" {
  alarm_name          = "ErrorLoggedWarn"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = aws_cloudwatch_log_metric_filter.error_logged.name
  namespace           = "covidportal"
  period              = "60"
  statistic           = "Sum"
  threshold           = "1"
  alarm_description   = "This metric monitors for an error level logs"

  alarm_actions = [aws_sns_topic.alert_warning.arn]
}

resource "aws_cloudwatch_log_metric_filter" "fatal_logged" {
  name           = "FatalLogged"
  pattern        = "level=fatal"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "FatalLogged"
    namespace = "covidportal"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "fatal_logged_warn" {
  alarm_name          = "FatalLoggedWarn"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = aws_cloudwatch_log_metric_filter.fatal_logged.name
  namespace           = "covidportal"
  period              = "60"
  statistic           = "Sum"
  threshold           = "1"
  alarm_description   = "This metric monitors for a fatal level logs"

  alarm_actions = [aws_sns_topic.alert_warning.arn, aws_sns_topic.alert_critical.arn]
}

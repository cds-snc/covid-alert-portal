resource "aws_cloudwatch_log_group" "qrcode" {
  name       = var.cloudwatch_log_group_name_qrcode
  kms_key_id = aws_kms_key.cw.arn

  tags = {
    (var.billing_tag_key) = var.billing_tag_value
  }
}

###
# AWS CloudWatch Metrics - Scaling metrics
###

resource "aws_cloudwatch_metric_alarm" "qrcode_cpu_utilization_high_warn" {
  alarm_name          = "CpuUtilizationWarn_qrcode"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization_qrcode"
  namespace           = "AWS/ECS"
  period              = "120"
  statistic           = "Average"
  threshold           = "50"
  alarm_description   = "QR Code registration Warning - High CPU usage has been detected."

  alarm_actions = [aws_sns_topic.alert_warning.arn]
  ok_actions    = [aws_sns_topic.alert_ok.arn]
  dimensions = {
    ClusterName = aws_ecs_cluster.covidportal.name
    ServiceName = aws_ecs_service.qrcode.name
  }
}

resource "aws_cloudwatch_metric_alarm" "qrcode_memory_utilization_high_warn" {
  alarm_name          = "MemoryUtilizationWarn_qrcode"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "MemoryUtilization_qrcode"
  namespace           = "AWS/ECS"
  period              = "120"
  statistic           = "Average"
  threshold           = "50"
  alarm_description   = "QR Code registration Warning - High memory usage has been detected."

  alarm_actions = [aws_sns_topic.alert_warning.arn]
  ok_actions    = [aws_sns_topic.alert_ok.arn]

  dimensions = {
    ClusterName = aws_ecs_cluster.covidportal.name
    ServiceName = aws_ecs_service.qrcode.name
  }
}


###
# AWS CloudWatch Metrics - Code errors
###

resource "aws_cloudwatch_log_metric_filter" "five_hundred_response_qrcode" {
  name           = "500Response_qrcode"
  pattern        = "\"HTTP/1.1 5\""
  log_group_name = aws_cloudwatch_log_group.qrcode.name

  metric_transformation {
    name          = "500Response_qrcode"
    namespace     = "qrcode"
    value         = "1"
    default_value = "0"
  }
}

resource "aws_cloudwatch_metric_alarm" "five_hundred_response_warn_qrcode" {
  alarm_name          = "500ResponseWarn_qrcode"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = aws_cloudwatch_log_metric_filter.five_hundred_response_qrcode.name
  namespace           = "qrcode"
  period              = "60"
  statistic           = "Sum"
  threshold           = "0"
  treat_missing_data  = "notBreaching"
  alarm_description   = "QR Code registration Warning - A 5xx HTML error was detected coming from the portal."

  alarm_actions = [aws_sns_topic.alert_warning.arn]
}

resource "aws_cloudwatch_log_metric_filter" "application_error_qrcode" {
  name           = "ApplicationError_qrcode"
  pattern        = "Error"
  log_group_name = aws_cloudwatch_log_group.qrcode.name

  metric_transformation {
    name          = "ApplicationError"
    namespace     = "qrcode"
    value         = "1"
    default_value = "0"
  }
}

resource "aws_cloudwatch_metric_alarm" "application_error_warn_qrcode" {
  alarm_name          = "ApplicationError_qrcode"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = aws_cloudwatch_log_metric_filter.application_error_qrcode.name
  namespace           = "qrcode"
  period              = "60"
  statistic           = "Sum"
  threshold           = "0"
  treat_missing_data  = "notBreaching"
  alarm_description   = "QR Code registration Warning - An error message was detected in the ECS logs"

  alarm_actions = [aws_sns_topic.alert_warning.arn]
}

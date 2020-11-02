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

resource "aws_cloudwatch_metric_alarm" "portal_cpu_utilization_high_warn" {
  alarm_name          = "CpuUtilizationWarn"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "120"
  statistic           = "Average"
  threshold           = "50"
  alarm_description   = "COVID Alert Portal Warning - High CPU usage has been detected."

  alarm_actions = [aws_sns_topic.alert_warning.arn]
  dimensions = {
    ClusterName = aws_ecs_cluster.covidportal.name
    ServiceName = aws_ecs_service.covidportal.name
  }
}

resource "aws_cloudwatch_metric_alarm" "portal_memory_utilization_high_warn" {
  alarm_name          = "MemoryUtilizationWarn"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = "120"
  statistic           = "Average"
  threshold           = "50"
  alarm_description   = "COVID Alert Portal Warning - High memory usage has been detected."

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
  pattern        = "\"HTTP/1.1 5\""
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name          = "500Response"
    namespace     = "covidportal"
    value         = "1"
    default_value = "0"
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
  threshold           = "0"
  treat_missing_data  = "notBreaching"
  alarm_description   = "COVID Alert Portal Warning - A 5xx HTML error was detected coming from the portal."

  alarm_actions = [aws_sns_topic.alert_warning.arn]
}

resource "aws_cloudwatch_log_metric_filter" "application_error" {
  name           = "ApplicationError"
  pattern        = "Error"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name          = "ApplicationError"
    namespace     = "covidportal"
    value         = "1"
    default_value = "0"
  }
}

resource "aws_cloudwatch_metric_alarm" "application_error_warn" {
  alarm_name          = "ApplicationErrorWarn"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = aws_cloudwatch_log_metric_filter.application_error.name
  namespace           = "covidportal"
  period              = "60"
  statistic           = "Sum"
  threshold           = "0"
  treat_missing_data  = "notBreaching"
  alarm_description   = "COVID Alert Portal Warning - An error message was detected in the ECS logs"

  alarm_actions = [aws_sns_topic.alert_warning.arn]
}


###
# AWS CloudWatch Metrics - Activity Alarms
###

resource "aws_cloudwatch_log_metric_filter" "key_generation" {
  name           = "KeyGeneration"
  pattern        = "\"CRUD event_type:CREATE model:covid_key.covidkey\""
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name          = "KeyGeneration"
    namespace     = "covidportal"
    value         = "1"
    default_value = "0"
  }
}

resource "aws_cloudwatch_metric_alarm" "key_generation_warn" {
  alarm_name          = "KeyGenerationWarn"
  comparison_operator = "GreaterThanThreshold"
  metric_name         = aws_cloudwatch_log_metric_filter.key_generation.name
  namespace           = "covidportal"
  period              = "3600"
  statistic           = "Sum"
  evaluation_periods  = "1"
  threshold           = "20"
  treat_missing_data  = "notBreaching"
  alarm_description   = "COVID Alert Portal Warning - COVID one-time keys generation is 50% of the way to alarm status (x keys / hour)."
  alarm_actions       = [aws_sns_topic.alert_warning.arn]
}

resource "aws_cloudwatch_metric_alarm" "key_generation_critical" {
  alarm_name          = "KeyGenerationCritical"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = aws_cloudwatch_log_metric_filter.key_generation.name
  namespace           = "covidportal"
  period              = "3600"
  statistic           = "Sum"
  threshold           = "40"
  treat_missing_data  = "notBreaching"
  alarm_description   = "COVID Alert Portal Critical - COVID one-time keys generation alarm threshold surpassed (x keys / hour)."
  alarm_actions       = [aws_sns_topic.alert_critical.arn]
}

resource "aws_cloudwatch_log_metric_filter" "site_change" {
  name           = "SiteTableChange"
  pattern        = "\"CRUD\" \"model:sites.site\""
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name          = "SiteTableChange"
    namespace     = "covidportal"
    value         = "1"
    default_value = "0"
  }
}

resource "aws_cloudwatch_metric_alarm" "site_change_warn" {
  alarm_name          = "SiteTableChangeWarn"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = aws_cloudwatch_log_metric_filter.site_change.name
  namespace           = "covidportal"
  period              = "60"
  statistic           = "Sum"
  threshold           = "0"
  treat_missing_data  = "notBreaching"
  alarm_description   = "COVID Alert Portal Warning - Someone changed something on the Django sites table."
  alarm_actions       = [aws_sns_topic.alert_warning.arn]
}

resource "aws_cloudwatch_log_metric_filter" "account_lockout" {
  name           = "AccountLockout"
  pattern        = "\"AXES: Locking out\""
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name          = "AccountLockout"
    namespace     = "covidportal"
    value         = "1"
    default_value = "0"
  }
}

resource "aws_cloudwatch_metric_alarm" "account_lockout_warn" {
  alarm_name          = "AccountLockoutWarn"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = aws_cloudwatch_log_metric_filter.account_lockout.name
  namespace           = "covidportal"
  period              = "3600"
  statistic           = "Sum"
  threshold           = "4"
  treat_missing_data  = "notBreaching"
  alarm_description   = "COVID Alert Portal Warning - Multiple user accounts have been locked out in the last hour (x locked accounts / hour)."
  alarm_actions       = [aws_sns_topic.alert_warning.arn]
}

resource "aws_cloudwatch_log_metric_filter" "invite_lockout" {
  name           = "InviteLockout"
  pattern        = "\"Forbidden: /en/invite/\""
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name          = "InviteLockout"
    namespace     = "covidportal"
    value         = "1"
    default_value = "0"
  }
}

resource "aws_cloudwatch_metric_alarm" "invite_lockout_warn" {
  alarm_name          = "InviteLockoutWarn"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = aws_cloudwatch_log_metric_filter.invite_lockout.name
  namespace           = "covidportal"
  period              = "60"
  statistic           = "Sum"
  threshold           = "0"
  treat_missing_data  = "notBreaching"
  alarm_description   = "COVID Alert Portal Warning - Someone has tried to invite more users than permitted (x invites / hour)."
  alarm_actions       = [aws_sns_topic.alert_warning.arn]
}

###
# AWS Metrics for Service Down Alarms
###

resource "aws_cloudwatch_metric_alarm" "response_time_warn" {
  alarm_name          = "ResponseTimeWarn"
  comparison_operator = "GreaterThanUpperThreshold"
  evaluation_periods  = "2"
  threshold_metric_id = "e1"
  alarm_description   = "COVID Alert Portal Warning - The latency of response times from the Portal are abnormally high."
  treat_missing_data  = "notBreaching"
  alarm_actions       = [aws_sns_topic.alert_warning.arn]

  metric_query {
    id          = "e1"
    expression  = "ANOMALY_DETECTION_BAND(m1, 3)"
    label       = "Response Times (Expected)"
    return_data = "true"
  }

  metric_query {
    id          = "m1"
    return_data = "true"
    metric {
      metric_name = "TargetResponseTime"
      namespace   = "AWS/ApplicationELB"
      period      = "60"
      stat        = "Average"
      dimensions = {
        LoadBalancer = aws_lb.covidportal.arn_suffix
      }
    }
  }
}

resource "aws_cloudwatch_log_metric_filter" "service_availability" {
  name           = "ServiceAvailability"
  pattern        = "\"GET /status/ => generated\""
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name          = "ServiceAvailability"
    namespace     = "covidportal"
    value         = "1"
    default_value = "0"
  }
}

resource "aws_cloudwatch_metric_alarm" "service_availability_warn" {
  alarm_name          = "ServiceAvailabilityWarn"
  comparison_operator = "LessThanLowerThreshold"
  evaluation_periods  = "1"
  threshold_metric_id = "e1"
  alarm_description   = "COVID Alert Portal Warning - No status checks detected.  Check COVID Alert Portal to ensure site is operational."
  treat_missing_data  = "breaching"
  alarm_actions       = [aws_sns_topic.alert_warning.arn]

  metric_query {
    id          = "e1"
    expression  = "ANOMALY_DETECTION_BAND(m1, 3)"
    label       = "Status Checks (Expected)"
    return_data = "true"
  }

  metric_query {
    id          = "m1"
    return_data = "true"
    metric {
      metric_name = "ServiceAvailability"
      namespace   = "covidportal"
      period      = "60"
      stat        = "Sum"
    }
  }
}

###
# AWS CloudWatch Metrics - DDoS Alarms
###

resource "aws_cloudwatch_metric_alarm" "ddos_detected_covidportal_warn" {
  alarm_name          = "DDoSDetectedCovidPortalWarn"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "DDoSDetected"
  namespace           = "AWS/DDoSProtection"
  period              = "60"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "COVID Alert Portal Warning - AWS has detected a DDOS attack on the COVID Alert Portal's Load Balancer"

  alarm_actions = [aws_sns_topic.alert_warning.arn]

  dimensions = {
    ResourceArn = aws_lb.covidportal.arn
  }
}

resource "aws_cloudwatch_metric_alarm" "ddos_detected_route53_warn" {

  alarm_name          = "DDoSDetectedRoute53Warn"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "DDoSDetected"
  namespace           = "AWS/DDoSProtection"
  period              = "60"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "COVID Alert Portal Warning - AWS has detected a DDOS attack on the COVID Alert Portal's DNS Server"

  alarm_actions = [aws_sns_topic.alert_warning.arn]

  dimensions = {
    ResourceArn = "arn:aws:route53:::hostedzone/${aws_route53_zone.covidportal.zone_id}"
  }
}

###
# AWS CodeDeploy Events
###

resource "aws_cloudwatch_event_target" "codedeploy_sns" {
  target_id = "CodeDeploy_SNS"
  rule      = aws_cloudwatch_event_rule.codedeploy_sns.name
  arn       = aws_sns_topic.alert_warning.arn

  input_transformer {
    input_paths = {
      "status"       = "$.detail.state"
      "deploymentID" = "$.detail.deploymentId"
    }
    input_template = "\"COVID Alert Portal Warning - CloudDeploy has registered a <status> for deployment: <deploymentID>\""
  }
}

resource "aws_cloudwatch_event_rule" "codedeploy_sns" {
  name        = "alert-on-codedeploy-status"
  description = "Alert if CodeDeploy Fails during deployment"

  event_pattern = <<PATTERN
  {
    "source": [
      "aws.codedeploy"
    ],
    "detail-type": [
      "CodeDeploy Deployment State-change Notification"
    ],
    "detail": {
      "state": [
        "FAILURE"
      ]
    }
  }
  PATTERN
}

###
# AWS Metrics for Security Dashboard Reporting
###

# Metric to help track suspicious login times
resource "aws_cloudwatch_log_metric_filter" "users_login" {
  name           = "UsersLogin"
  pattern        = "\"LOGIN login_type:login\""
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name          = "UsersLogin"
    namespace     = "covidportal"
    value         = "1"
    default_value = "0"
  }
}


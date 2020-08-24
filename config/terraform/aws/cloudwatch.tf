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
  alarm_description   = "Covid Alert Portal - This metric monitors ecs cpu utilization"

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
  alarm_description   = "Covid Alert Portal - This metric monitors ecs memory utilization"

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
  pattern        = "\"HTTP/1.1 ?500 ?501 ?502 ?503 ?504 ?505 ?506 ?507 ?508 ?510 ?511\""
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
  treat_missing_data  = "notBreaching"
  alarm_description   = "Covid Alert Portal - This metric monitors for an 5xx level response"

  alarm_actions = [aws_sns_topic.alert_warning.arn]
}

resource "aws_cloudwatch_log_metric_filter" "application_error" {
  name           = "ApplicationError"
  pattern        = "ERROR"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "ApplicationError"
    namespace = "covidportal"
    value     = "1"
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
  threshold           = "1"
  treat_missing_data  = "notBreaching"
  alarm_description   = "Covid Alert Portal - This metric monitors for an Application error"

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
    name      = "KeyGeneration"
    namespace = "covidportal"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "key_generation_warn" {
  alarm_name          = "KeyGenerationWarn"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = aws_cloudwatch_log_metric_filter.key_generation.name
  namespace           = "covidportal"
  period              = "3600"
  statistic           = "Sum"
  threshold           = "11"
  treat_missing_data  = "notBreaching"
  alarm_description   = "COVID Alert Portal - This metric monitors for more then 11 keys generated in a hour"
  alarm_actions       = [aws_sns_topic.alert_warning.arn]
}

resource "aws_cloudwatch_log_metric_filter" "site_change" {
  name           = "SiteTableChange"
  pattern        = "\"CRUD model:sites.site\""
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "SiteTableChange"
    namespace = "covidportal"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "site_change_warn" {
  alarm_name          = "SiteChangeWarn"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = aws_cloudwatch_log_metric_filter.site_change.name
  namespace           = "covidportal"
  period              = "60"
  statistic           = "Sum"
  threshold           = "1"
  treat_missing_data  = "notBreaching"
  alarm_description   = "COVID Alert Portal - This metric monitors for any site table changes"
  alarm_actions       = [aws_sns_topic.alert_warning.arn]
}

resource "aws_cloudwatch_log_metric_filter" "account_lockout" {
  name           = "AccountLockout"
  pattern        = "\"AXES: Locking out\""
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "AccountLockout"
    namespace = "covidportal"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "AccountLockoutWarn" {
  alarm_name          = "AccountLockoutWarn"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = aws_cloudwatch_log_metric_filter.account_lockout.name
  namespace           = "covidportal"
  period              = "3600"
  statistic           = "Sum"
  threshold           = "5"
  treat_missing_data  = "notBreaching"
  alarm_description   = "COVID Alert Portal - This metric monitors for more than 5 locked out accounts in an hour"
  alarm_actions       = [aws_sns_topic.alert_warning.arn]
}

resource "aws_cloudwatch_log_metric_filter" "invite_lockout" {
  name           = "InviteLockout"
  pattern        = "\"Forbidden: /en/invite/\""
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "InviteLockout"
    namespace = "covidportal"
    value     = "1"
  }
}

resource "aws_cloudwatch_metric_alarm" "InviteLockoutWarn" {
  alarm_name          = "InviteLockoutWarn"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = aws_cloudwatch_log_metric_filter.invite_lockout.name
  namespace           = "covidportal"
  period              = "60"
  statistic           = "Sum"
  threshold           = "1"
  treat_missing_data  = "notBreaching"
  alarm_description   = "COVID Alert Portal - This metric montiors for too many invitations by a user"
  alarm_actions       = [aws_sns_topic.alert_warning.arn]
}

###
# AWS CloudWatch Metrics - DDoS Alarms
###

resource "aws_cloudwatch_metric_alarm" "ddos_detected_covidportal" {
  alarm_name          = "DDoSDetectedCovidPortal"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "DDoSDetected"
  namespace           = "AWS/DDoSProtection"
  period              = "60"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "Covid Alert Portal - This metric monitors for DDoS detected on Covid Portal ALB"

  alarm_actions = [aws_sns_topic.alert_critical.arn]

  dimensions = {
    ResourceArn = aws_lb.covidportal.arn
  }
}

resource "aws_cloudwatch_metric_alarm" "ddos_detected_route53" {

  alarm_name          = "DDoSDetectedRoute53"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "DDoSDetected"
  namespace           = "AWS/DDoSProtection"
  period              = "60"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "Covid Alert Portal - This metric monitors for DDoS detected on route 53"

  alarm_actions = [aws_sns_topic.alert_critical.arn]

  dimensions = {
    ResourceArn = "arn:aws:route53:::hostedzone/${aws_route53_zone.covidportal.zone_id}"
  }
}

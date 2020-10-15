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

# Alberta User Metric
resource "aws_cloudwatch_log_metric_filter" "alberta_super_admins" {
  name           = "AlbertaSuperAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=Alberta, saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "AlbertaSuperAdmins"
    namespace = "covidportal"
    value     = "$super_admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "alberta_admins" {
  name           = "AlbertaAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=Alberta, saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "AlbertaAdmins"
    namespace = "covidportal"
    value     = "$admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "alberta_staff" {
  name           = "AlbertaStaff"
  pattern        = "[date, time, type=LOGGING, ..., province=Alberta, saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "AlbertaStaff"
    namespace = "covidportal"
    value     = "$staff"
  }
}

# BC User Metric

resource "aws_cloudwatch_log_metric_filter" "bc_super_admins" {
  name           = "BCSuperAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=\"British Columbia\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "BCSuperAdmins"
    namespace = "covidportal"
    value     = "$super_admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "bc_admins" {
  name           = "BCAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=\"British Columbia\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "BCAdmins"
    namespace = "covidportal"
    value     = "$admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "bc_staff" {
  name           = "BCStaff"
  pattern        = "[date, time, type=LOGGING, ..., province=\"British Comumbia\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "BCStaff"
    namespace = "covidportal"
    value     = "$staff"
  }
}
# Canadian Armed Forces User Metric
resource "aws_cloudwatch_log_metric_filter" "caf_super_admins" {
  name           = "CAFSuperAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Canadian Armed Forces\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "CAFSuperAdmins"
    namespace = "covidportal"
    value     = "$super_admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "caf_admins" {
  name           = "CAFAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Canadian Armed Forces\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "CAFAdmins"
    namespace = "covidportal"
    value     = "$admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "caf_staff" {
  name           = "CAFStaff"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Canadian Armed Forces\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "CAFStaff"
    namespace = "covidportal"
    value     = "$staff"
  }
}

# Canadian Digital Service User Metric
resource "aws_cloudwatch_log_metric_filter" "cds_super_admins" {
  name           = "CDSSuperAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Canadian Digital Service\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "CDSSuperAdmins"
    namespace = "covidportal"
    value     = "$super_admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "cds_admins" {
  name           = "CDSAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Canadian Digital Service\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "CDSAdmins"
    namespace = "covidportal"
    value     = "$admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "cds_staff" {
  name           = "CDSStaff"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Canadian Digital Service\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "CDSStaff"
    namespace = "covidportal"
    value     = "$staff"
  }
}

# Manitoba User Metric

resource "aws_cloudwatch_log_metric_filter" "manitoba_super_admins" {
  name           = "ManitobaSuperAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Manitoba\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "ManitobaSuperAdmins"
    namespace = "covidportal"
    value     = "$super_admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "manitoba_admins" {
  name           = "ManitobaAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Manitoba\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "ManitobaAdmins"
    namespace = "covidportal"
    value     = "$admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "manitoba_staff" {
  name           = "ManitobaStaff"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Canadian Digital Service\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "ManitobaStaff"
    namespace = "covidportal"
    value     = "$staff"
  }
}

# New Brunswick User Metric

resource "aws_cloudwatch_log_metric_filter" "nb_super_admins" {
  name           = "NBSuperAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=\"New Brunswick\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "NBSuperAdmins"
    namespace = "covidportal"
    value     = "$super_admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "nb_admins" {
  name           = "NBSAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=\"New Brunswick\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "NBAdmins"
    namespace = "covidportal"
    value     = "$admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "nb_staff" {
  name           = "NBStaff"
  pattern        = "[date, time, type=LOGGING, ..., province=\"New Brunswick\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "NBStaff"
    namespace = "covidportal"
    value     = "$staff"
  }
}

# Newfoundland and Labrador User Metric
resource "aws_cloudwatch_log_metric_filter" "nfld_super_admins" {
  name           = "NFLDSuperAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Newfoundland and Labrador\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "NFLDSuperAdmins"
    namespace = "covidportal"
    value     = "$super_admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "nfld_admins" {
  name           = "NFLDAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Newfoundland and Labrador\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "NFLDAdmins"
    namespace = "covidportal"
    value     = "$admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "nfld_staff" {
  name           = "NFLDStaff"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Newfoundland and Labrador\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "NFLDStaff"
    namespace = "covidportal"
    value     = "$staff"
  }
}
# Nova Scotia User Metric
resource "aws_cloudwatch_log_metric_filter" "ns_super_admins" {
  name           = "NSSuperAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Nova Scotia\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "NSSuperAdmins"
    namespace = "covidportal"
    value     = "$super_admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "ns_admins" {
  name           = "NSAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Nova Scotia\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "NSAdmins"
    namespace = "covidportal"
    value     = "$admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "ns_staff" {
  name           = "NSStaff"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Nova Scotia\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "NSStaff"
    namespace = "covidportal"
    value     = "$staff"
  }
}
# Northwest Territories User Metric
resource "aws_cloudwatch_log_metric_filter" "nwt_super_admins" {
  name           = "NWTSuperAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Northwest Territories\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "NWTSuperAdmins"
    namespace = "covidportal"
    value     = "$super_admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "nwt_admins" {
  name           = "NWTAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Northwest Territories\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "CDSAdmins"
    namespace = "covidportal"
    value     = "$admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "nwt_staff" {
  name           = "NWTStaff"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Northwest Territories\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "NWTStaff"
    namespace = "covidportal"
    value     = "$staff"
  }
}
# Nunavut User Metric
resource "aws_cloudwatch_log_metric_filter" "nunavut_super_admins" {
  name           = "NunavutSuperAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Nunavut\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "NunavutSuperAdmins"
    namespace = "covidportal"
    value     = "$super_admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "nunavut_admins" {
  name           = "NunavutAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Nunavut\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "NunavutAdmins"
    namespace = "covidportal"
    value     = "$admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "nunavut_staff" {
  name           = "NunavutStaff"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Nunavut\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "NunavutStaff"
    namespace = "covidportal"
    value     = "$staff"
  }
}
# Ontario User Metric
resource "aws_cloudwatch_log_metric_filter" "ontario_super_admins" {
  name           = "OntarioSuperAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Ontario\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "OntarioSuperAdmins"
    namespace = "covidportal"
    value     = "$super_admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "ontario_admins" {
  name           = "OntarioAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Ontario\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "OntarioAdmins"
    namespace = "covidportal"
    value     = "$admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "ontario_staff" {
  name           = "OntarioStaff"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Ontario\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "OntarioStaff"
    namespace = "covidportal"
    value     = "$staff"
  }
}
# Prince Edward Island User Metric
resource "aws_cloudwatch_log_metric_filter" "pei_super_admins" {
  name           = "PEISuperAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Prince Edward Island\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "PEISuperAdmins"
    namespace = "covidportal"
    value     = "$super_admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "pei_admins" {
  name           = "PEIAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Prince Edward Island\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "PEIAdmins"
    namespace = "covidportal"
    value     = "$admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "pei_staff" {
  name           = "PEIStaff"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Prince Edward Island\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "PEIStaff"
    namespace = "covidportal"
    value     = "$staff"
  }
}
# Quebec User Metric
resource "aws_cloudwatch_log_metric_filter" "quebec_super_admins" {
  name           = "QuebecSuperAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Quebec\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "QuebecSuperAdmins"
    namespace = "covidportal"
    value     = "$super_admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "quebec_admins" {
  name           = "QuebecAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Quebec\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "QuebecAdmins"
    namespace = "covidportal"
    value     = "$admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "quebec_staff" {
  name           = "QuebecStaff"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Quebec\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "QuebecStaff"
    namespace = "covidportal"
    value     = "$staff"
  }
}
# Saskatchewan User Metric
resource "aws_cloudwatch_log_metric_filter" "sask_super_admins" {
  name           = "SaskatchewanSuperAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Saskatchewan\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "SaskatchewanSuperAdmins"
    namespace = "covidportal"
    value     = "$super_admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "sask_admins" {
  name           = "SaskatchewanAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Saskatchewan\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "SaskatchewanAdmins"
    namespace = "covidportal"
    value     = "$admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "sask_staff" {
  name           = "SaskatchewanStaff"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Saskatchewan\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "SaskatchewanStaff"
    namespace = "covidportal"
    value     = "$staff"
  }
}
# Yukon User Metric
resource "aws_cloudwatch_log_metric_filter" "yukon_super_admins" {
  name           = "YukonSuperAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Yukon\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "YukonSuperAdmins"
    namespace = "covidportal"
    value     = "$super_admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "yukon_admins" {
  name           = "YukonAdmins"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Yukon\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "YukonAdmins"
    namespace = "covidportal"
    value     = "$admins"
  }
}

resource "aws_cloudwatch_log_metric_filter" "yukon_staff" {
  name           = "YukonStaff"
  pattern        = "[date, time, type=LOGGING, ..., province=\"Yukon\", saText, super_admins, aText, admins, sText, staff]"
  log_group_name = aws_cloudwatch_log_group.covidportal.name

  metric_transformation {
    name      = "YukonStaff"
    namespace = "covidportal"
    value     = "$staff"
  }
}
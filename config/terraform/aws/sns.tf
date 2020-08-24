resource "aws_sns_topic" "alert_warning" {
  name              = "alert-warning"
  kms_master_key_id = aws_kms_key.cw.arn

  tags = {
    (var.billing_tag_key) = var.billing_tag_value
  }
}

resource "aws_sns_topic" "alert_critical" {
  name              = "alert-critical"
  kms_master_key_id = aws_kms_key.cw.arn

  tags = {
    (var.billing_tag_key) = var.billing_tag_value
  }
}

resource "aws_sns_topic_subscription" "topic_warning" {
  topic_arn = aws_sns_topic.alert_warning.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.notify_slack_sns.arn
}

resource "aws_sns_topic_subscription" "topic_critical" {
  topic_arn = aws_sns_topic.alert_critical.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.notify_slack_sns.arn
}
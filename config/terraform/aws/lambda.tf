###
# AWS Lambda - Notifiy Slack
###

resource "aws_iam_role" "iam_for_notify_slack" {
  name = "iam_for_lambda"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

data "archive_file" "notify_slack_sns" {
  type        = "zip"
  source_file = "lambda/lambda_notify_slack.js"
  output_path = "/tmp/lambda_notify_slack.js.zip"
}

resource "aws_lambda_function" "notify_slack_sns" {
  filename      = "/tmp/lambda_notify_slack.js.zip"
  function_name = "NotifySlackSNS"
  role          = aws_iam_role.iam_for_notify_slack.arn
  handler       = "lambda_notify_slack.handler"

  source_code_hash = data.archive_file.notify_slack_sns.output_base64sha256

  runtime = "nodejs12.x"

  environment {
    variables = {
      SLACK_WEBHOOK = var.slack_webhook
    }
  }

}
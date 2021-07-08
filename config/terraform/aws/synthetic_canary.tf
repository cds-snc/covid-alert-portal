#
# Synthetic canary
#

resource "aws_synthetics_canary" "qr_code_status" {
  name                 = "qr-code-status"
  artifact_s3_location = "s3://${aws_s3_bucket.synthetic_artifacts.id}/qr-code-canary/"
  execution_role_arn   = aws_iam_role.synthetic_canary_execution_role.arn
  zip_file             = data.archive_file.canary_qr_code_status.output_path
  handler              = "healthcheck.handler"
  runtime_version      = "syn-nodejs-puppeteer-3.1"
  start_canary         = true

  schedule {
    expression = "rate(5 minutes)"
  }
}

resource "random_uuid" "qr_code_status_zip" {
  keepers = {
    "template" : sha256(data.template_file.canary_qr_code_status.rendered)
  }
}

data "template_file" "canary_qr_code_status" {
  template = file("synthetic_canary/healthcheck.tmpl.js")
  vars = {
    healthcheck_url_en = "https://register.covid-hcportal.cdssandbox.xyz/status/"
    healthcheck_url_fr = "https://register.covid-hcportal.cdssandbox.xyz/status/"
  }
}

data "archive_file" "canary_qr_code_status" {
  type = "zip"
  source {
    content  = data.template_file.canary_qr_code_status.rendered
    filename = "nodejs/node_modules/healthcheck.js"
  }
  output_path = "${random_uuid.qr_code_status_zip.result}.js.zip"
}

#
# S3 bucket for canary artifacts
#

resource "aws_s3_bucket" "synthetic_artifacts" {

  # tfsec:ignore:AWS077 Don't need to version these as they expire and are ephemeral
  # tfsec:ignore:AWS002 Logging not required on ephemeral data

  bucket = "covid-portal-synthetic-artifacts-${var.environment}"
  acl    = "private"
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
  lifecycle_rule {
    enabled = true
    expiration {
      days = 31
    }
  }
}

resource "aws_s3_bucket_public_access_block" "qr_code_canary" {
  bucket = aws_s3_bucket.synthetic_artifacts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

#
# Canary execution role and policy
#

resource "aws_iam_role" "synthetic_canary_execution_role" {
  name               = "synthetic_canary_role"
  assume_role_policy = data.aws_iam_policy_document.synthetic_canary_assume_role_policy.json
}

resource "aws_iam_policy" "synthetic_canary_policy" {
  name   = "SyntheticCanaryPolicy"
  path   = "/"
  policy = data.aws_iam_policy_document.synthetic_canary_policy.json
}

resource "aws_iam_role_policy_attachment" "synthetic_canary_policy_attachment" {
  role       = aws_iam_role.synthetic_canary_execution_role.name
  policy_arn = aws_iam_policy.synthetic_canary_policy.arn
}

data "aws_iam_policy_document" "synthetic_canary_assume_role_policy" {
  statement {
    effect = "Allow"
    actions = [
      "sts:AssumeRole"
    ]
    principals {
      type = "Service"
      identifiers = [
        "lambda.amazonaws.com"
      ]
    }
  }
}

data "aws_iam_policy_document" "synthetic_canary_policy" {
  statement {
    effect = "Allow"
    actions = [
      "s3:PutObject",
      "s3:GetBucketLocation"
    ]
    resources = [
      aws_s3_bucket.synthetic_artifacts.arn,
      "${aws_s3_bucket.synthetic_artifacts.arn}/*"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:CreateLogGroup"
    ]
    resources = [
      "arn:aws:logs:${var.region}:${data.aws_caller_identity.current.id}:log-group:/aws/lambda/cwsyn-${aws_synthetics_canary.qr_code_status.name}-*"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "s3:ListAllMyBuckets",
      "xray:PutTraceSegments"
    ]
    resources = [
      "*"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "cloudwatch:PutMetricData"
    ]
    resources = [
      "*"
    ]
    condition {
      test     = "StringEquals"
      variable = "cloudwatch:namespace"
      values = [
        "CloudWatchSynthetics"
      ]
    }
  }
}

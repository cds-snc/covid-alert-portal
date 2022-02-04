locals {
  cbs_satellite_bucket_name   = "${var.cbs_satellite_bucket_name_prefix}${data.aws_caller_identity.current.account_id}"
  cbs_satellite_bucket_arn    = "arn:aws:s3:::${local.cbs_satellite_bucket_name}"
  cbs_satellite_bucket_prefix = "waf_acl_logs/AWSLogs/${data.aws_caller_identity.current.account_id}/"
}

###
# AWS Kinesis Firehose - IAM Role
###
resource "aws_iam_role" "firehose_waf_logs" {
  name = "firehose_waf_logs"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "firehose.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

###
# AWS Kinesis Firehose - IAM Policy
###
resource "aws_iam_role_policy" "firehose_waf_logs" {
  name   = "firehose-waf-logs-policy"
  role   = aws_iam_role.firehose_waf_logs.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Action": [
        "s3:AbortMultipartUpload",
        "s3:GetBucketLocation",
        "s3:GetObject",
        "s3:ListBucket",
        "s3:ListBucketMultipartUploads",
        "s3:PutObject"
      ],
      "Resource": [
        "${local.cbs_satellite_bucket_arn}",
        "${local.cbs_satellite_bucket_arn}/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": "iam:CreateServiceLinkedRole",
      "Resource": "arn:aws:iam::*:role/aws-service-role/wafv2.amazonaws.com/AWSServiceRoleForWAFV2Logging"
    }
  ]
}
EOF
}

###
# AWS Kinesis Firehose - Delivery Stream
###
resource "aws_kinesis_firehose_delivery_stream" "firehose_waf_logs" {
  name        = "aws-waf-logs-covid-portal"
  destination = "extended_s3"

  server_side_encryption {
    enabled = true
  }

  extended_s3_configuration {
    role_arn           = aws_iam_role.firehose_waf_logs.arn
    prefix             = local.cbs_satellite_bucket_prefix
    bucket_arn         = local.cbs_satellite_bucket_arn
    compression_format = "GZIP"
  }
}

resource "aws_kinesis_firehose_delivery_stream" "firehose_waf_logs_qrcode" {
  name        = "aws-waf-logs-qrcode"
  destination = "extended_s3"

  server_side_encryption {
    enabled = true
  }

  extended_s3_configuration {
    role_arn           = aws_iam_role.firehose_waf_logs.arn
    prefix             = local.cbs_satellite_bucket_prefix
    bucket_arn         = local.cbs_satellite_bucket_arn
    compression_format = "GZIP"
  }
}
###
# AWS S3 bucket - WAF log target
###
resource "aws_s3_bucket" "firehose_waf_logs" {
  bucket = "staging-covid-portal-terraform-waf-logs"
  acl    = "private"
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
  #tfsec:ignore:AWS002
  #tfsec:ignore:AWS077
}

resource "aws_s3_bucket" "firehose_waf_logs_qrcode" {
  bucket = "staging-qrcode-terraform-waf-logs"
  acl    = "private"
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
  #tfsec:ignore:AWS002
  #tfsec:ignore:AWS077
}

###
# AWS S3 bucket - Maintenance mode HTML

resource "aws_s3_bucket" "portal_maintenance_mode" {
  bucket = "staging-covid-portal-maintenance-mode"
  acl    = "private"
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
  #tfsec:ignore:AWS002
  #tfsec:ignore:AWS077
}

resource "aws_s3_bucket_object" "html_files" {
  for_each      = fileset("./maintenance_mode/", "*.htm")
  content_type  = "text/html"
  bucket        = "staging-covid-portal-maintenance-mode"
  key           = each.value
  source        = "./maintenance_mode/${each.value}"
  etag          = filemd5("./maintenance_mode/${each.value}")
  cache_control = "max-age=60"
}

resource "aws_s3_bucket_object" "html_supporting_css" {
  for_each     = fileset("./maintenance_mode/", "*.css")
  content_type = "text/css"
  bucket       = "staging-covid-portal-maintenance-mode"
  key          = each.value
  source       = "./maintenance_mode/${each.value}"
  etag         = filemd5("./maintenance_mode/${each.value}")
}

resource "aws_s3_bucket_object" "html_supporting_svg" {
  for_each     = fileset("./maintenance_mode/", "*.svg")
  content_type = "image/svg+xml"
  bucket       = "staging-covid-portal-maintenance-mode"
  key          = each.value
  source       = "./maintenance_mode/${each.value}"
  etag         = filemd5("./maintenance_mode/${each.value}")
}

resource "aws_s3_bucket_object" "html_supporting_ico" {
  for_each     = fileset("./maintenance_mode/", "*.ico")
  content_type = "image/png"
  bucket       = "staging-covid-portal-maintenance-mode"
  key          = each.value
  source       = "./maintenance_mode/${each.value}"
  etag         = filemd5("./maintenance_mode/${each.value}")
}

data "aws_iam_policy_document" "web_distribution" {
  statement {
    actions = ["s3:GetObject"]
    principals {
      type        = "AWS"
      identifiers = [aws_cloudfront_origin_access_identity.maintenance_access_identity.iam_arn]
    }
    resources = ["${aws_s3_bucket.portal_maintenance_mode.arn}/*"]
  }
}

resource "aws_s3_bucket_policy" "web_distribution" {
  bucket = aws_s3_bucket.portal_maintenance_mode.id
  policy = data.aws_iam_policy_document.web_distribution.json
}

###
# AWS S3 bucket - cloudfront log target
###
resource "aws_s3_bucket" "cloudfront_logs" {

  # tfsec:ignore:AWS002 Logging not required in Staging
  # tfsec:ignore:AWS077 Don't need to version these they should expire and are ephemeral

  bucket = "covid-portal-${var.environment}-cloudfront-logs"
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
      days = 90
    }
  }

  # awslogsdelivery account needs full control for cloudfront logging
  # https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/AccessLogs.html#AccessLogsBucketAndFileOwnership
  grant {
    id          = "c4c1ede66af53448b93c283ce9448c4ba468c9432aa01d700d3878632f77d2d0"
    type        = "CanonicalUser"
    permissions = ["FULL_CONTROL"]
  }
}

resource "aws_s3_bucket_public_access_block" "cloudfront_logs" {
  bucket = aws_s3_bucket.cloudfront_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
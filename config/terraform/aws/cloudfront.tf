locals {
  s3_origin_id = "MaintenanceModeHTML"
}

resource "aws_cloudfront_origin_access_identity" "maintenance_access_identity" {
  comment = "Access Identity for the Maintenance Website"
}

#tfsec:ignore:AWS071
resource "aws_cloudfront_distribution" "maintenance_mode" {
  http_version = "http2"

  web_acl_id = aws_wafv2_web_acl.maintenancepage_acl.arn

  origin {
    origin_id   = local.s3_origin_id
    domain_name = aws_s3_bucket.portal_maintenance_mode.bucket_regional_domain_name
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.maintenance_access_identity.cloudfront_access_identity_path
    }

  }
  enabled             = true
  comment             = "This will host the maintenance mode site for COVID Alert Portal"
  default_root_object = "en.htm"
  aliases             = ["portal.covid-hcportal.cdssandbox.xyz", "register.covid-hcportal.cdssandbox.xyz"]

  default_cache_behavior {
    compress         = true
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = local.s3_origin_id

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }
    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  custom_error_response {
    error_code         = "403"
    response_code      = "200"
    response_page_path = "/en.htm"
  }
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate_validation.cert.certificate_arn
    minimum_protocol_version = "TLSv1.2_2021"
    ssl_support_method       = "sni-only"
  }

  price_class = "PriceClass_100"

  depends_on = [
    aws_s3_bucket.portal_maintenance_mode
  ]
}

###
# AWS Cloudfront (CDN) - QR code
###

resource "aws_cloudfront_distribution" "qrcode" {
  origin {
    domain_name = aws_lb.qrcode.dns_name
    origin_id   = aws_lb.qrcode.name

    custom_header {
      name  = "covidqrcode"
      value = var.cloudfront_qrcode_custom_header
    }

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  enabled         = true
  is_ipv6_enabled = true
  web_acl_id      = aws_wafv2_web_acl.qrcode_cdn_acl.arn

  aliases = ["register.covid-hcportal.cdssandbox.xyz"]

  # By default, cache nothing (controlled by TTL of 0)
  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT", "DELETE"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = aws_lb.qrcode.name

    forwarded_values {
      query_string = true
      headers      = ["Referer"]
      cookies {
        forward = "all"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 0
    compress               = true
  }

  # Cache `/static/*` assets for 1 week
  # Cache busting has been added to the asset filenames to keep requests fresh
  ordered_cache_behavior {
    path_pattern     = "/static/*"
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = aws_lb.qrcode.name

    forwarded_values {
      query_string = true
      headers      = ["Referer"]
      cookies {
        forward = "all"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 604800 # 1 week
    default_ttl            = 604800
    max_ttl                = 604800
    compress               = true
  }

  price_class = "PriceClass_100"

  restrictions {
    geo_restriction {
      restriction_type = "whitelist"
      locations        = ["CA", "US"]
    }
  }

  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate_validation.cert.certificate_arn
    minimum_protocol_version = "TLSv1.2_2021"
    ssl_support_method       = "sni-only"
  }

  logging_config {
    include_cookies = false
    bucket          = aws_s3_bucket.cloudfront_logs.bucket_domain_name
    prefix          = "cloudfront"
  }

  depends_on = [aws_s3_bucket.cloudfront_logs]
}
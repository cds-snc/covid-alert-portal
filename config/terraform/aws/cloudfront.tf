locals {
  s3_origin_id = "MaintenanceModeHTML"
}

resource "aws_cloudfront_origin_access_identity" "maintenance_access_identity" {
  comment = "Access Identity for the Maintenance Website"
}

resource "aws_cloudfront_distribution" "maintenance_mode" {
  http_version = "http2"

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
  aliases             = ["staging.covid-hcportal.cdssandbox.xyz"]

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
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }
  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate.covidportal_maintenance.arn
    minimum_protocol_version = "TLSv1.2_2019"
    ssl_support_method       = "sni-only"
  }

  depends_on = [
    aws_s3_bucket.portal_maintenance_mode
  ]
}
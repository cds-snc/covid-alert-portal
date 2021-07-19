###
# Route53 Zone
###

resource "aws_route53_zone" "covidportal" {
  name = var.route53_zone_name

  tags = {
    (var.billing_tag_key) = var.billing_tag_value
  }
}

###
# Route53 Record - Covid Portal
###

resource "aws_route53_record" "covidportal" {
  zone_id = aws_route53_zone.covidportal.zone_id
  name    = "portal.${aws_route53_zone.covidportal.name}"
  type    = "A"

  set_identifier = "main"

  failover_routing_policy {
    type = "PRIMARY"
  }

  alias {
    name                   = aws_lb.covidportal.dns_name
    zone_id                = aws_lb.covidportal.zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "covidportal_maintenance" {
  zone_id = aws_route53_zone.covidportal.zone_id
  name    = aws_route53_record.covidportal.name
  type    = "A"

  set_identifier = "backup"

  failover_routing_policy {
    type = "SECONDARY"
  }

  alias {
    name                   = aws_cloudfront_distribution.maintenance_mode.domain_name
    zone_id                = aws_cloudfront_distribution.maintenance_mode.hosted_zone_id
    evaluate_target_health = false
  }
}

# Route 53 Healthcheck
resource "aws_route53_health_check" "dns-is-routeable" {
  fqdn              = "portal.${aws_route53_zone.covidportal.name}"
  port              = 443
  type              = "HTTPS"
  resource_path     = "/status/"
  failure_threshold = "5"
  request_interval  = "30"
}

#################################################################
# Repeat the same configuration for a QR Code registration domain
#################################################################


resource "aws_route53_record" "qrcode" {
  zone_id = aws_route53_zone.covidportal.zone_id
  name    = "register.${aws_route53_zone.covidportal.name}"
  type    = "A"

  set_identifier = "main"

  failover_routing_policy {
    type = "PRIMARY"
  }

  alias {
    name                   = aws_lb.qrcode.dns_name
    zone_id                = aws_lb.qrcode.zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "maintenance_qrcode" {
  zone_id = aws_route53_zone.covidportal.zone_id
  name    = aws_route53_record.qrcode.name
  type    = "A"

  set_identifier = "backup"

  failover_routing_policy {
    type = "SECONDARY"
  }

  alias {
    name                   = aws_cloudfront_distribution.maintenance_mode.domain_name
    zone_id                = aws_cloudfront_distribution.maintenance_mode.hosted_zone_id
    evaluate_target_health = false
  }
}

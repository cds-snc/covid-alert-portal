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
  name    = "staging.${aws_route53_zone.covidportal.name}"
  type    = "A"

  set_identifier  = "main"
  health_check_id = aws_route53_health_check.up_or_down.id

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
    evaluate_target_health = true
  }
}

resource "aws_route53_health_check" "up_or_down" {
  fqdn              = "staging.covid-hcportal.cdssandbox.xyz"
  enable_sni        = true
  port              = 443
  type              = "HTTPS"
  resource_path     = "/status/"
  failure_threshold = "3"
  request_interval  = "10"
}
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
  name    = "production.${aws_route53_zone.covidportal.name}"
  type    = "CNAME"

  alias {
    name                   = aws_lb.covidportal.dns_name
    zone_id                = aws_lb.covidportal.zone_id
    evaluate_target_health = false
  }
}

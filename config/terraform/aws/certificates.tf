resource "aws_acm_certificate" "covidportal" {
  domain_name               = "covid-alert-portal.alpha.canada.ca"
  subject_alternative_names = ["portail-alerte-covid.alpha.canada.ca"]
  validation_method         = "DNS"

  tags = {
    (var.billing_tag_key) = var.billing_tag_value
  }

  lifecycle {
    create_before_destroy = true
  }
}


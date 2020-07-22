###
# AWS IPSet - list of IPs/CIDRs to allow
###
resource "aws_wafv2_ip_set" "new_key_claim" {
  name               = "new-key-claim"
  description        = "New Key Claim Allow IPs/CIDRs"
  scope              = "REGIONAL"
  ip_address_version = "IPV4"
  addresses          = toset(var.new_key_claim_allow_list)
}

resource "aws_wafv2_web_acl" "covidportal" {
  name  = "covid_portal"
  scope = "REGIONAL"

  default_action {
    allow {}
  }

  tags = {
    (var.billing_tag_key) = var.billing_tag_value
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "covid_portal"
    sampled_requests_enabled   = false
  }
}

###
# AWS WAF - Resource Assocation
###

resource "aws_wafv2_web_acl_association" "covid_portal_assocation" {
  resource_arn = aws_lb.covidportal.arn
  web_acl_arn  = aws_wafv2_web_acl.covidportal.arn
}

###
# AWS WAF - Logging
###

resource "aws_wafv2_web_acl_logging_configuration" "firehose_waf_logs_portal" {
  log_destination_configs = ["${aws_kinesis_firehose_delivery_stream.firehose_waf_logs.arn}"]
  resource_arn            = aws_wafv2_web_acl.covidportal.arn
}

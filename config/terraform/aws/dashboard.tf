
resource "aws_cloudwatch_dashboard" "ocio_report" {
  dashboard_name = "SecurityReport"

  dashboard_body = <<EOF
{
    "widgets": [
        {
            "type": "metric",
            "x": 0,
            "y": 1,
            "width": 6,
            "height": 3,
            "properties": {
                "metrics": [
                    [ "covidportal", "KeyGeneration" ]
                ],
                "view": "singleValue",
                "region": "ca-central-1",
                "stat": "Sum",
                "period": 300,
                "setPeriodToTimeRange": true,
                "title": "Total Keys Generated"
            }
        },
        {
            "type": "metric",
            "x": 6,
            "y": 1,
            "width": 9,
            "height": 6,
            "properties": {
                "metrics": [
                    [ { "expression": "m1-m1+MAX(m1)", "label": "Max OTK's in time period", "id": "e1", "region": "ca-central-1" } ],
                    [ "covidportal", "KeyGeneration", { "id": "m1" } ]
                ],
                "view": "timeSeries",
                "region": "ca-central-1",
                "stat": "Sum",
                "period": 86400,
                "stacked": false,
                "title": "Keys Generated per day"
            }
        },
        {
            "type": "metric",
            "x": 15,
            "y": 1,
            "width": 9,
            "height": 6,
            "properties": {
                "title": "Key Generation Critical Alarm",
                "annotations": {
                    "alarms": [
                        "arn:aws:cloudwatch:ca-central-1:595701125956:alarm:KeyGenerationCritical"
                    ]
                },
                "view": "timeSeries",
                "stacked": true
            }
        },
        {
            "type": "text",
            "x": 0,
            "y": 0,
            "width": 24,
            "height": 1,
            "properties": {
                "markdown": "\n# Portal Activity\n"
            }
        },
        {
            "type": "metric",
            "x": 0,
            "y": 8,
            "width": 9,
            "height": 6,
            "properties": {
                "metrics": [
                    [ "AWS/WAFV2", "BlockedRequests", "WebACL", "covid_portal", "Region", "ca-central-1", "Rule", "LoginPageRateLimit", { "label": "Login Page Rate Limiter" } ],
                    [ "...", "PostRequestRateLimit", { "label": "Post Request Rate Limiter" } ],
                    [ "...", "AWSManagedRulesLinuxRuleSet", { "label": "Linux Rule Set" } ],
                    [ "...", "AWSManagedRulesKnownBadInputsRuleSet", { "label": "Known Bad Inputs" } ],
                    [ "...", "AWSManagedRulesCommonRuleSet", { "label": "Common Rule Set" } ],
                    [ "...", "AWSManagedRulesAmazonIpReputationList", { "label": "Ip Reputation List" } ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "ca-central-1",
                "stat": "Sum",
                "period": 86400,
                "title": "WAF Blocked Requests"
            }
        },
        {
            "type": "text",
            "x": 0,
            "y": 7,
            "width": 24,
            "height": 1,
            "properties": {
                "markdown": "\n# Web Application Firewall (WAF)\n"
            }
        },
        {
            "type": "log",
            "x": 15,
            "y": 8,
            "width": 9,
            "height": 6,
            "properties": {
                "query": "SOURCE 'covidportal_staging' | fields @message\n| filter @message like /LOGIN login_type:login/\n| parse @message \"LOGIN login_type:login user_id:* remote_ip:*\" as userID, remoteIP\n| stats count_distinct(userID) as NumberOfUsers by remoteIP\n| filter (NumberOfUsers>1)",
                "region": "ca-central-1",
                "stacked": false,
                "title": "Multiple Users per IP",
                "view": "table"
            }
        },
        {
            "type": "metric",
            "x": 9,
            "y": 8,
            "width": 6,
            "height": 6,
            "properties": {
                "view": "pie",
                "stacked": true,
                "metrics": [
                    [ "AWS/WAFV2", "BlockedRequests", "WebACL", "covid_portal", "Region", "ca-central-1", "Rule", "ALL" ],
                    [ ".", "AllowedRequests", ".", ".", ".", ".", ".", "." ]
                ],
                "region": "ca-central-1",
                "setPeriodToTimeRange": true,
                "title": "Allowed vs Blocked Requests"
            }
        },
        {
            "type": "log",
            "x": 0,
            "y": 4,
            "width": 6,
            "height": 3,
            "properties": {
                "query": "SOURCE 'covidportal_staging' | fields @message\n| filter @message like /model:profiles.healthcareuser/\n| parse @message \"CRUD event_type:* model:profiles.healthcareuser\" as action\n| stats sum(strcontains(action, \"CREATE\")) as CreatedUsers, sum(strcontains(action,\"DELETE\")) as DeletedUsers\n",
                "region": "ca-central-1",
                "stacked": false,
                "title": "User Activity",
                "view": "table"
            }
        }
    ]
}
EOF
}
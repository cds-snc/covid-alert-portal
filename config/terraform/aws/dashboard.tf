
resource "aws_cloudwatch_dashboard" "ocio_report" {
  dashboard_name = "SecurityReport"

  dashboard_body = <<EOF
{
    "start": "-P7D",
    "widgets": [
        {
            "type": "log",
            "x": 0,
            "y": 29,
            "width": 15,
            "height": 6,
            "properties": {
                "query": "SOURCE 'covidportal_staging' | fields @message\n| filter @message like /HTTP\\/1.1 400/ and @message not like /\\/status/\n| parse @message \"() {*} [*] * * => generated\" toss1, toss2, method, url\n| filter url != \"/\"\n| stats concat(method,\" \", url) as path, count(path) as attempts by path\n| sort by attempts desc",
                "region": "ca-central-1",
                "stacked": false,
                "title": "Attempts that passed WAF but returned HTML Error 400 from COVID Alert Portal",
                "view": "table"
            }
        },
        {
            "type": "log",
            "x": 0,
            "y": 13,
            "width": 12,
            "height": 9,
            "properties": {
                "query": "SOURCE 'covidportal_staging' | fields @timestamp, @message\n| filter @message like /LOGGING user_count/\n| parse @message '* LOGGING user_count province: \"*\" super_admins: * admins: * staff: *' logtime, province, super_admins, admins, staff\n| sort @timestamp desc\n| limit 15\n| display province, super_admins, admins, staff\n\n\n",
                "region": "ca-central-1",
                "stacked": false,
                "title": "User type by Province",
                "view": "table"
            }
        },
        {
            "type": "log",
            "x": 15,
            "y": 23,
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
            "type": "log",
            "x": 0,
            "y": 10,
            "width": 6,
            "height": 3,
            "properties": {
                "query": "SOURCE 'covidportal_staging' | fields @message\n| filter @message like /model:profiles.healthcareuser/\n| parse @message \"CRUD event_type:* model:profiles.healthcareuser\" as action\n| stats sum(strcontains(action, \"CREATE\")) as CreatedUsers, sum(strcontains(action,\"DELETE\")) as DeletedUsers\n",
                "region": "ca-central-1",
                "stacked": false,
                "title": "Total User Modification Actiivty",
                "view": "table"
            }
        },
        {
            "type": "metric",
            "x": 0,
            "y": 7,
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
            "y": 7,
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
            "y": 7,
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
            "y": 6,
            "width": 24,
            "height": 1,
            "properties": {
                "markdown": "\n# Portal Activity\n"
            }
        },
        {
            "type": "metric",
            "x": 0,
            "y": 23,
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
            "y": 22,
            "width": 24,
            "height": 1,
            "properties": {
                "markdown": "\n# Web Application Firewall (WAF)\n"
            }
        },
        {
            "type": "metric",
            "x": 9,
            "y": 23,
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
            "type": "text",
            "x": 0,
            "y": 0,
            "width": 24,
            "height": 3,
            "properties": {
                "markdown": "\n# Dashboard Generation Indicator\nWhen the majority of the bars in the graph below are at or near the '100' value the dashboard is completely loaded.\n\nThis amount of time is required to ensure that the 'User Activity', 'Multiple Users / IP', and 'Attempts that succeeded WAF but were blocked by COVID Alert Portal' have enough time to completely load.\n"
            }
        },
        {
            "type": "metric",
            "x": 12,
            "y": 13,
            "width": 12,
            "height": 9,
            "properties": {
                "metrics": [
                    [ "covidportal", "UsersLogin", { "id": "m1", "stat": "Sum", "label": "UserLogins", "period": 3600 } ],
                    [ { "expression": "ANOMALY_DETECTION_BAND(m1, 2)", "label": "AnomalyBand", "id": "e1", "region": "ca-central-1" } ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "ca-central-1",
                "stat": "Average",
                "period": 300,
                "title": "User Login Anomolay Detection Band"
            }
        },
        {
            "type": "log",
            "x": 0,
            "y": 3,
            "width": 24,
            "height": 3,
            "properties": {
                "query": "SOURCE 'covidportal_staging' | fields @message\n| filter @message like /\\/status\\//\n| stats (count()/51500)*100 as Analysis_Progress by bin (1d)",
                "region": "ca-central-1",
                "stacked": false,
                "title": "Report Generation Progress Indicator",
                "view": "bar"
            }
        }
    ]
}
EOF
}
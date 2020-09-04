var https = require('https');
var util = require('util');

exports.handler = function(event, context) {

    var postData = {
        "channel": "#exposure-healthcare-dev",
        "username": "COVID Alert Portal Notifier",
        "text": "*Staging Environment*",
        "icon_emoji": ":loudspeaker:"
    };

    var message = "AlarmDescription" in event.Records[0].Message ? event.Records[0].Message.AlarmDescription : event.Records[0].Sns.Message;
    var severity = "good";

    var dangerMessages = [
        "COVID Alert Portal Critical"
      ];

    var warningMessages = [
        "COVID Alert Portal Warning"
        ];
    
    for(var dangerMessagesItem in dangerMessages) {
        if (message.indexOf(dangerMessages[dangerMessagesItem]) != -1) {
            severity = "danger";
            postData.icon_emoji = ":rotating_light:";
            break;
        }
    }
    
    // Only check for warning messages if necessary
    if (severity == "good") {
        for(var warningMessagesItem in warningMessages) {
            if (message.indexOf(warningMessages[warningMessagesItem]) != -1) {
                severity = "warning";
                postData.icon_emoji = ":warning:";
                break;
            }
        }        
    }

    postData.attachments = [
        {
            "color": severity, 
            "text": message
        }
    ];

    var options = {
        method: 'POST',
        hostname: 'hooks.slack.com',
        port: 443,
        path: process.env.SLACK_WEBHOOK
    };

    var req = https.request(options, function(res) {
      res.setEncoding('utf8');
      res.on('data', function (chunk) {
        context.done(null);
      });
    });
    
    req.on('error', function(e) {
      console.log('problem with request: ' + e.message);
    });    

    req.write(util.format("%j", postData));
    req.end();
};
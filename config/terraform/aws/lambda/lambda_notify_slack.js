var https = require('https');
var util = require('util');

function getMessage(message) {
    try {
        const parsedMessage = JSON.parse(message);
        return parsedMessage.AlarmDescription ? parsedMessage.AlarmDescription : parsedMessage;
    } catch(err) {
        return message;
    }

}
exports.handler = function(event, context) {

    var postData = {
        "channel": "#exposure-healthcare-dev",
        "username": "COVID Alert Portal Notifier",
        "text": "*Staging Environment*",
        "icon_emoji": ":loudspeaker:"
    };

    var message = event.Records[0].Sns.Message;

    var severity = "good";
    var needs_processing = true;

    var dangerMessages = [
        "COVID Alert Portal Critical"
      ];

    var warningMessages = [
        "COVID Alert Portal Warning"
        ];

    var okMessages = [
        "\"NewStateValue\":\"OK\""
    ];

    
    for(var okMessagesItem in okMessages) {
        if (message.indexOf(okMessages[okMessagesItem]) != -1) {
            message = "Alarm Status now OK - " + getMessage(message); 
            needs_processing = false;
            break;
        }
    }
    
    // Only check for critial messages if necessary
    if (needs_processing){
        for(var dangerMessagesItem in dangerMessages) {
            if (message.indexOf(dangerMessages[dangerMessagesItem]) != -1) {
                severity = "danger";
                postData.icon_emoji = ":rotating_light:";
                message = getMessage(message);
                needs_processing = false;
                break;
            }
        }
    }

    
    // Only check for warning messages if necessary
    if (needs_processing) {
        for(var warningMessagesItem in warningMessages) {
            if (message.indexOf(warningMessages[warningMessagesItem]) != -1) {
                severity = "warning";
                postData.icon_emoji = ":warning:";
                message = getMessage(message);
                needs_processing = false;
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
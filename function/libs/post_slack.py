# https://api.slack.com/messaging/webhooks#getting_started
import json
from urllib import request


def main(title: str, detail: str, url: str) -> None:
    url = url
    payload = {
        "text": title,
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": title
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ":aws-logo:  *サービス別利用料金*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": detail
                }
            },
            {
                "type": "divider"
            }
        ]
    }
    data = json.dumps(payload).encode()

    req = request.Request(url, data=data, method='POST')
    with request.urlopen(req) as response:
        print(response.status)

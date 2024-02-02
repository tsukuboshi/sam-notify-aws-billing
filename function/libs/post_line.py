# https://notify-bot.line.me/doc/ja/
from urllib import request, parse


def main(title: str, detail: str, token: str) -> None:
    url = "https://notify-api.line.me/api/notify"
    payload = {
        "message": f"{title}\n\n{detail}"
        }
    data = parse.urlencode(payload).encode("utf-8")
    headers = {"Authorization": "Bearer %s" % token}

    req = request.Request(url, data=data, headers=headers, method='POST')
    with request.urlopen(req) as response:
        print(response.status)

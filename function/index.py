import json
import logging
import os
from datetime import date, datetime, timedelta
from typing import Tuple
from urllib import parse, request

import boto3

logger = logging.getLogger()
logger.setLevel(logging.getLevelName(os.getenv("LOG_LEVEL", "INFO")))


# Lambdaのエントリーポイント
def lambda_handler(event, context) -> None:
    client = boto3.client("ce", region_name="us-east-1")

    # 合計とサービス毎の請求額を取得する
    total_billing = get_total_billing(client)
    service_billings = get_service_billings(client)

    # 投稿用のメッセージを作成する
    (title, detail) = create_message(total_billing, service_billings)

    try:
        # SlackのWebhook URLが設定されている場合は、Slackにメッセージを投稿する
        if os.environ.get("SLACK_WEBHOOK_URL_PATH"):
            url = get_secret(os.environ.get("SLACK_WEBHOOK_URL_PATH"), "info")

            logger.info("Post message to slack...")
            url = url
            payload = {
                "text": title,
                "blocks": [
                    {"type": "header", "text": {"type": "plain_text", "text": title}},
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": ":aws-logo:  *サービス別利用料金*"},
                    },
                    {"type": "section", "text": {"type": "mrkdwn", "text": detail}},
                    {"type": "divider"},
                ],
            }
            data = json.dumps(payload).encode()

            send_request(url, data)

        # LINEのアクセストークンが設定されている場合は、LINEにメッセージを投稿する
        if os.environ.get("LINE_ACCESS_TOKEN_PATH"):
            logger.info("Get line access token...")
            token = get_secret(os.environ.get("LINE_ACCESS_TOKEN_PATH"), "info")

            logger.info("Post message to line...")
            url = "https://notify-api.line.me/api/notify"
            payload = {"message": f"{title}\n\n{detail}"}
            data = parse.urlencode(payload).encode("utf-8")
            headers = {"Authorization": "Bearer %s" % token}

            send_request(url, data, headers)

        # いずれの送信先も設定されていない場合はエラーを出力する
        if not os.environ.get("SLACK_WEBHOOK_URL_PATH") and not os.environ.get("LINE_ACCESS_TOKEN_PATH"):
            logger.error("No destination to post message. Please set environment variables.")

    except Exception as e:
        logger.exception("Exception occurred: %s", e)
        raise e


# 合計の請求額を取得する関数
def get_total_billing(client) -> dict:
    (start_date, end_date) = get_total_cost_date_range()

    response = client.get_cost_and_usage(
        TimePeriod={"Start": start_date, "End": end_date},
        Granularity="MONTHLY",
        Metrics=["AmortizedCost"],
    )
    return {
        "start": response["ResultsByTime"][0]["TimePeriod"]["Start"],
        "end": response["ResultsByTime"][0]["TimePeriod"]["End"],
        "billing": response["ResultsByTime"][0]["Total"]["AmortizedCost"]["Amount"],
    }


# サービス毎の請求額を取得する関数
def get_service_billings(client) -> list:
    (start_date, end_date) = get_total_cost_date_range()

    response = client.get_cost_and_usage(
        TimePeriod={"Start": start_date, "End": end_date},
        Granularity="MONTHLY",
        Metrics=["AmortizedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )

    billings = []

    for item in response["ResultsByTime"][0]["Groups"]:
        billings.append(
            {
                "service_name": item["Keys"][0],
                "billing": item["Metrics"]["AmortizedCost"]["Amount"],
            }
        )
    return billings


# メッセージを作成する関数
def create_message(total_billing: dict, service_billings: list) -> Tuple[str, str]:
    start = datetime.strptime(total_billing["start"], "%Y-%m-%d").strftime("%m/%d")

    # Endの日付は結果に含まないため、表示上は前日にしておく
    end_today = datetime.strptime(total_billing["end"], "%Y-%m-%d")
    end_yesterday = (end_today - timedelta(days=1)).strftime("%m/%d")

    total = round(float(total_billing["billing"]), 2)

    title = f"{start}～{end_yesterday}の請求額：{total:.2f} USD"

    details = []
    for item in service_billings:
        service_name = item["service_name"]
        billing = round(float(item["billing"]), 2)

        if billing == 0.0:
            # 請求無し（0.0 USD）の場合は、内訳を表示しない
            continue
        details.append(f"・{service_name}: {billing:.2f} USD")

    return title, "\n".join(details)


# 請求額の期間を取得する関数
def get_total_cost_date_range() -> Tuple[str, str]:
    start_date = date.today().replace(day=1).isoformat()
    end_date = date.today().isoformat()

    # get_cost_and_usage()のstartとendに同じ日付は指定不可のため、
    # 「今日が1日」なら、「先月1日から今月1日（今日）」までの範囲にする
    if start_date == end_date:
        end_of_month = datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=-1)
        begin_of_month = end_of_month.replace(day=1)
        return begin_of_month.date().isoformat(), end_date
    return start_date, end_date


# シークレットマネージャからシークレットを取得する関数
def get_secret(secret_name: str, secret_key: str) -> str:
    secrets_extension_endpoint = (
        "http://localhost:2773/secretsmanager/get?secretId=" + secret_name
    )
    headers = {"X-Aws-Parameters-Secrets-Token": os.environ.get("AWS_SESSION_TOKEN")}
    secrets_extension_req = request.Request(secrets_extension_endpoint, headers=headers)
    with request.urlopen(secrets_extension_req) as response:
        secret_config = response.read()
    secret_json = json.loads(secret_config)["SecretString"]
    secret_value = json.loads(secret_json)[secret_key]
    return secret_value


# HTTPリクエストを送信する関数
def send_request(url: str, data: str, headers=None) -> None:
    req = request.Request(url, data=data, headers=headers, method="POST")
    with request.urlopen(req) as response:
        print(response.status)

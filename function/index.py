import logging
import os
from libs import get_billing, get_secret, post_slack, post_line

logger = logging.getLogger()
logger.setLevel(logging.getLevelName(os.getenv("LOG_LEVEL", "INFO")))


def handler(event, context) -> None:
    # 合計とサービス毎の請求額を取得し、メッセージを作成する
    logger.info('Get billing information...')
    (title, detail) = get_billing.main()

    try:
        # Slackにメッセージを投稿する
        if os.environ.get('SLACK_WEBHOOK_URL_PATH'):
            logger.info('Get slack webhook url...')
            url = get_secret.main(os.environ.get('SLACK_WEBHOOK_URL_PATH'), 'info')

            logger.info('Post message to slack...')
            post_slack.main(title, detail, url)

        # LINEにメッセージを投稿する
        if os.environ.get('LINE_ACCESS_TOKEN_PATH'):
            logger.info('Get line access token...')
            token = get_secret.main(os.environ.get('LINE_ACCESS_TOKEN_PATH'), 'info')

            logger.info('Post message to line...')
            post_line.main(title, detail, token)

    except Exception as e:
        logger.exception("Exception occurred: %s", e)
        raise e

# sam-notify-aws-billing

## 概要

Email/Slack/LINEのいずれかに対して、以下のメッセージ形式でAWS請求額を通知します。

- タイトル

```md
AWS請求額通知(mm/dd～mm/dd) : <合計請求額> USD
```

- 本文

```
・<サービス名>: <サービス請求額> USD
・<サービス名>: <サービス請求額> USD
...
```

## 構成図

![diagram](./image/diagram.drawio.png)

## デプロイ方法

1. (Slackで通知したい場合)以下を参考にWebhook URLを取得する

[Sending messages using incoming webhooks \| Slack](https://api.slack.com/messaging/webhooks)

2. (LINEで通知したい場合)以下を参考にPerspnal Access Tokenを取得する

[ヘルプセンター \| LINE Notify](https://help2.line.me/line_notify/web/?lang=ja)

3. 本リポジトリをクローン

``` bash
git clone https://github.com/tsukuboshi/sam-notify-aws-billing.git
cd sam-notify-aws-billing
```

4. 以下コマンドで、SAMアプリをビルド

``` bash
sam build
```

5. 以下コマンドで、SAMアプリをデプロイ

- Emailの場合

``` bash
sam deploy --parameter-overrides \
  EmailAddress=<Address>
```

- Slackの場合

``` bash
sam deploy --parameter-overrides \
  SlackWebhookUrl=<WebHookURL>
```

- LINEの場合

``` bash
sam deploy --parameter-overrides \
  LineAccessToken=<AccessToken>
```

6. (Emailで通知したい場合)以下を参考に、SNSトピックに対するEmailのサブスクリプションを承認する

[ステップ 3: サブスクリプションを確認する \- Amazon Simple Notification Service](https://docs.aws.amazon.com/ja_jp/sns/latest/dg/SendMessageToHttp.confirm.html)

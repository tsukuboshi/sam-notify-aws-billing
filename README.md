# sam-notify-aws-billing

## 概要

Mail/Slack/LINEのいずれかに対して、メッセージ形式でAWS利用料金を通知します。

## 構成図

![diagram](./image/diagram.drawio.png)

## SAMデプロイ方法

1. 以下コマンドで、SAMアプリをビルド

``` bash
sam build
```

2. 以下コマンドで、SAMアプリをデプロイ

- メールの場合

``` bash
sam deploy --parameter-overrides \
  EmailAddress=xxx
```

- Slackの場合

``` bash
sam deploy --parameter-overrides \
  SlackWebhookUrl=xxx
```

- LINEの場合

``` bash
sam deploy --parameter-overrides \
  LineAccessToken=xxx
```

import json
import os
from urllib import request


def main(secret_name: str, secret_key: str) -> str:
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

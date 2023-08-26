import json
import os
import time

import jwt
import requests
from dotenv import load_dotenv

url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"


def get_iamtoken():
    now = int(time.time())
    payload = {
        'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
        'iss': service_account_id,
        'iat': now,
        'exp': now + 360}
    encoded_token = jwt.encode(
        payload,
        private_key,
        algorithm='PS256',
        headers={'kid': key_id})
    response = requests.request("POST",
                                url,
                                headers={'Content-Type': 'application/json'},
                                data=json.dumps({"jwt": encoded_token}))

    return response.json()


def translate(texts: str, from_lang: str, to_lang: str):
    IAM_TOKEN = get_iamtoken()['iamToken']
    body = {
        "sourceLanguageCode": from_lang,
        "targetLanguageCode": to_lang,
        "texts": [texts],
        "folderId": catalog_id,
        "speller": True
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {0}".format(IAM_TOKEN)
    }
    response = requests.post('https://translate.api.cloud.yandex.net/translate/v2/translate',
                             json=body,
                             headers=headers
                             )

    return response.json()['translations'][0]['text']

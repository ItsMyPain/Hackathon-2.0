import json
import time
from datetime import datetime

import jwt
import openai
import requests
from flask import current_app


def update_iamtoken():
    iamtoken_exp = current_app.config.get('iamtoken_exp', datetime(2000, 1, 1))
    if iamtoken_exp < datetime.now():
        now = int(time.time())
        payload = {
            'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
            'iss': current_app.config.get('SERVICE_ACC_ID'),
            'iat': now,
            'exp': now + 360}
        encoded_token = jwt.encode(
            payload,
            current_app.config.get('PRIVATE_KEY'),
            algorithm='PS256',
            headers={'kid': current_app.config.get('PUBLIC_KEY_ID')})
        response = requests.request("POST",
                                    "https://iam.api.cloud.yandex.net/iam/v1/tokens",
                                    headers={'Content-Type': 'application/json'},
                                    data=json.dumps({"jwt": encoded_token}))
        data = response.json()
        current_app.config['iamtoken'] = data['iamToken']
        current_app.config['iamtoken_exp'] = datetime.strptime(data['expiresAt'][:19], '%Y-%m-%dT%H:%M:%S')

        print('Запрошен токен')


def translate(texts: str, from_lang: str, to_lang: str):
    update_iamtoken()
    body = {
        "sourceLanguageCode": from_lang,
        "targetLanguageCode": to_lang,
        "texts": [texts],
        "folderId": current_app.config.get('CATALOG_ID'),
        "speller": True
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {0}".format(current_app.config['iamtoken'])
    }
    response = requests.post('https://translate.api.cloud.yandex.net/translate/v2/translate',
                             json=body,
                             headers=headers
                             )

    return response.json()['translations'][0]['text']


def predict(text: str):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": text
            },
            # {
            #     "role": "user",
            #     "content": text
            # },
        ],
        temperature=1,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message.content

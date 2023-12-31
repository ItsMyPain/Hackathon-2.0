import json
import time
from datetime import datetime

import jwt
import openai
import requests
from flask import current_app


def update_iamtoken(num: int):
    iamtoken_exp = current_app.config.get(f'iamtoken_exp{num}', datetime(2000, 1, 1))
    if iamtoken_exp < datetime.now():
        now = int(time.time())
        payload = {
            'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
            'iss': current_app.config.get(f'SERVICE_ACC_ID{num}'),
            'iat': now,
            'exp': now + 360}
        encoded_token = jwt.encode(
            payload,
            current_app.config.get(f'PRIVATE_KEY{num}'),
            algorithm='PS256',
            headers={'kid': current_app.config.get(f'PUBLIC_KEY_ID{num}')})
        response = requests.request("POST",
                                    "https://iam.api.cloud.yandex.net/iam/v1/tokens",
                                    headers={'Content-Type': 'application/json'},
                                    data=json.dumps({"jwt": encoded_token}))

        if response.status_code != 200:
            raise Exception(response.text)

        data = response.json()
        current_app.config[f'iamtoken{num}'] = data['iamToken']
        current_app.config[f'iamtoken_exp{num}'] = datetime.strptime(data['expiresAt'][:19], '%Y-%m-%dT%H:%M:%S')

        print(f'Запрошен токен {num}')


def translate(texts: str, from_lang: str, to_lang: str) -> str:
    update_iamtoken(1)
    body = {
        "sourceLanguageCode": from_lang,
        "targetLanguageCode": to_lang,
        "texts": [texts],
        "folderId": current_app.config.get('CATALOG_ID'),
        "speller": True
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {current_app.config['iamtoken1']}"
    }
    response = requests.post("https://translate.api.cloud.yandex.net/translate/v2/translate",
                             json=body,
                             headers=headers
                             )
    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()['translations'][0]['text']


def predict_yandex(request_text: str, instruction: bool) -> str:
    update_iamtoken(2)
    body = {
        "model": "general",
        "instructionText": "Ты эксперт финансовой индустрии, контекст финансовой сферы, стиль формальный. Добавь роль, в качестве кого ты выступаешь, работая с этим запросом." if instruction else "",
        "requestText": request_text,
        "generationOptions": {
            "maxTokens": 300,
            "temperature": 0.01
        }
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {current_app.config['iamtoken2']}"
    }
    response = requests.post("https://llm.api.cloud.yandex.net/llm/v1alpha/instruct",
                             json=body,
                             headers=headers
                             )
    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()['result']['alternatives'][0]['text']


def summarize(text: str) -> str:
    mean_len = 10
    max_len = 130
    if len(text.split()) < mean_len:
        return text
    else:
        data = translate(text, 'ru', 'en')
        print()
        print('После перевода:', data)
        data = current_app.app_ctx_globals_class \
            .summarizer(data, max_length=max_len, min_length=mean_len, do_sample=False)[0]['summary_text']
        print()
        print('После суммаризатора:', data)
        data = translate(data, 'en', 'ru')
        print()
        print('После обратного перевода:', data)
        return data


def additional_text(text: str):
    return f"""Дополни исходный вопрос пользователя пятью уточняющими вопросами, исходя из контекста исходного вопроса, и сформулируй из них и исходного вопроса один расширенный вопрос.'{text}'"""


def predict_openai(text: str) -> str:
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

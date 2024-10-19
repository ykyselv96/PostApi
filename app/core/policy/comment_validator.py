import requests

# Ваш API ключ
api_key = "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"


# URL для обращения к API
url = "https://api.openai.com/v1/chat/completions"

# Заголовки для авторизации
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Данные запроса
data = {
    "model": "gpt-3.5-turbo",
    "messages": [
        {"role": "user", "content": "Как дела?"}
    ]
}

# Отправка POST-запроса
response = requests.post(url, headers=headers, json=data)

# Проверка ответа
if response.status_code == 200:

    response_data = response.json()
    print(response_data['choices'][0]['message']['content'])
else:
    print(f"Ошибка {response.status_code}: {response.text}")

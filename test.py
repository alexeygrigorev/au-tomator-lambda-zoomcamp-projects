import requests


url = 'https://3was74r7p9.execute-api.eu-west-1.amazonaws.com/create_repository'

create_repository_request = {
    'email': 'alexey@datatalks.club',
    'github': 'alexeygrigorev'
}

response = requests.post(url, json=create_repository_request)
print(response.json())
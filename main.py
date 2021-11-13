import http
import json
import os
from pathlib import Path

import requests
from requests import Response

from qna import verwerkersovereenkomst

token_url = 'http://localhost:5000/oauth/token'
client_url = 'http://localhost:5000/oauth/client'
contract_url = 'http://localhost:5000/contract'
user_url = 'http://localhost:5000/user'
template_url = 'http://localhost:5000/template'


def resource_owner_password_credentials_grant() -> Response:
    data = {
        'grant_type': 'password',
        'client_id': 'website',
        'username': os.environ['USERNAME'],
        'password': os.environ['PASSWORD'],
    }

    return requests.post(
        token_url,
        data=data,
    )


def get_api_client(token: str) -> Response:
    headers = {'Authorization': f'Bearer {token}'}
    return requests.get(client_url, headers=headers)


def client_credentials_grant(client_id: str, client_secret: str) -> Response:
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
    }

    return requests.post(
        token_url,
        data=data,
    )


def get_user_information(token: str) -> Response:
    headers = {'Authorization': f'Bearer {token}'}
    return requests.get(
        user_url,
        headers=headers
    )


def get_template(token: str, template_id: int) -> Response:
    headers = {'Authorization': f'Bearer {token}'}
    return requests.get(
        f'{template_url}/{template_id}',
        headers=headers
    )


def get_contract(token: str, contract_id: int) -> Response:
    headers = {'Authorization': f'Bearer {token}'}
    return requests.get(
        f'{contract_url}/{contract_id}',
        headers=headers
    )


def sign_contract(token: str, contract_id: int) -> Response:
    # Get the first user signature and use that one.
    signature = get_user_signatures(token).json()[0]['signature']

    # Get contract
    contract = get_contract(token, contract_id).json()
    data = {**contract['parties'][0], 'signature': signature}

    headers = {'Authorization': f'Bearer {token}'}
    return requests.put(
        f'{contract_url}/{contract_id}/sign',
        headers=headers,
        data=json.dumps(data)
    )


def get_user_signatures(token: str) -> Response:
    headers = {'Authorization': f'Bearer {token}'}
    return requests.get(
        f'{user_url}/signatures',
        headers=headers
    )


def extract_questions_from_template(template: dict):
    sections = template['sections']
    questions_list = []

    for section in sections:
        questions_list += section['questions']

    flat_questions_list: list = []

    for question in questions_list:
        flat_questions_list.append(
            {'id': question['id'], 'question': question['question'], 'options': question['options']})

    return flat_questions_list


def download_contract(token: str, contract_id: int):
    authorize = {'Authorization': f'Bearer {token}'}
    accept_pdf = {
        'Accept': 'application/pdf'
    }
    response = requests.get(
        contract_url + f'/{contract_id}/download',
        headers=authorize | accept_pdf | {'pragma': 'no-cache', 'cache-control': 'no-cache'}
    )

    path = './out'
    Path(path).mkdir(parents=True, exist_ok=True)
    with open(f'{path}/contract.pdf', 'wb') as file:
        file.write(response.content)

    print(f'Contract with id {contract_id} has been downloaded to {path}/contract.pdf')


def get_invite_link(token: str):
    invite_link = get_contract(token, contract_id).json()['parties'][1]['link']
    return f'http://localhost:8000/ondertekenen/{invite_link}'


def create_contract(token: str, template_id: int) -> int:
    authorize = {'Authorization': f'Bearer {token}'}
    content_type_json = {
        'Content-Type': 'application/json'
    }

    template = get_template(token, template_id).json()
    parties = template['parties']

    user = get_user_information(access_token).json()
    user_id = user['id']

    data = json.dumps({
        'name': template['name'],
        'templateId': template_id,
        'parties': [
            {
                'partyId': parties[0]['id'],
                'type': parties[0]['type'],
                'userId': user_id,
            },
            {
                'partyId': parties[1]['id'],
                'type': parties[1]['type'],
                'userId': None,
            }
        ],
        'answers': verwerkersovereenkomst,
        'callbackUrl': 'http://localhost:8080/callback',
    })

    response = requests.post(
        contract_url,
        headers=authorize | content_type_json,
        data=data
    )
    assert response.status_code == http.HTTPStatus.CREATED

    contract_id = response.json()['id']
    name = response.json()['name']
    print(f'Contract {name} with id {contract_id} has been created')

    return contract_id


def get_access_token() -> str:
    response = resource_owner_password_credentials_grant()
    print(response)
    response = get_api_client(response.json()['access_token'])

    # The previous steps do not need to be taken when copying the `client_id` and `client_secret` from the dashboard.
    response = client_credentials_grant(response.json()['client_id'], response.json()['client_secret'])
    access_token = response.json()['access_token']
    print(f'Access token: {access_token}')
    return access_token


if __name__ == '__main__':
    access_token = get_access_token()

    # template = get_template(access_token, 107)
    # print(json.dumps(extract_questions_from_template(template.json()), indent=4, sort_keys=True))

    # Create a contract
    contract_id = create_contract(access_token, 107)

    response = sign_contract(access_token, contract_id)
    assert response.status_code == http.HTTPStatus.OK

    print(get_invite_link(access_token))

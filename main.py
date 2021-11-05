import http
import json
import os
from pathlib import Path

import requests
from requests import Response

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


def create_contract(token: str, template_id: int) -> str:
    authorize = {'Authorization': f'Bearer {token}'}
    content_type_json = {
        'Content-Type': 'application/json'
    }
    accept_pdf = {
        'Accept': 'application/pdf'
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
        'answers': [
            {
                'questionId': 1333,
                # Wat is de volledige bedrijfsnaam van Opdrachtgever?
                'answer': 'd-centralize geo B.V. | Pro6PP'
            },
            {
                'questionId': 1334,
                # Wat is de plaatsnaam waar de Opdrachtgever is gevestigd?
                'answer': 'Eindhoven'
            },
            {
                'questionId': 1335,
                # Wat is de straatnaam?
                'answer': 'Klokgebouw'
            },
            {
                'questionId': 1336,
                # Wat is het nummer van het handelsregister van de Kamer van Koophandel (KvK) van Opdrachtgever?
                'answer': '64589900'
            },
            {
                'questionId': 1337,
                # Is de ondertekenaar van Opdrachtgever een man of een vrouw?
                'answer': ' de heer'
            },
            {
                'questionId': 1338,
                # Hoedanigheid ondertekenaar Opdrachtgever: is deze ingeschreven als bestuurder of
                # gevolmachtigde in de kamer van koophandel?
                'answer': 'gevolmachtigde'
            },
            {
                'questionId': 1339,
                # Wat is de volledige bedrijfsnaam van de Opdrachtnemer?
                'answer': 'Tech company b.v.'
            },
            {
                'questionId': 1340,
                # Wat is de plaatsnaam waar de Opdrachtnemer is gevestigd?
                'answer': 'Amsterdam'
            },
            {
                'questionId': 1341,
                # Wat is de straatnaam? (Opdrachtnemer)
                'answer': 'leidseplein'
            },
            {
                'questionId': 1342,
                # Wat is het nummer van het handelsregister van de Kamer van Koophandel (KvK) van Opdrachtnemer?
                'answer': '00000000'
            },
            {
                'questionId': 1343,
                # Is de ondertekenaar van Opdrachtnemer een man of een vrouw?
                'answer': 'Mevrouw'
            },
            {
                'questionId': 1344,
                # Hoedanigheid ondertekenaar Opdrachtnemer: is deze ingeschreven als bestuurder of
                # gevolmachtigde in de kamer van koophandel?
                'answer': 'bestuurder'
            },
            {
                'questionId': 1345,
                # Wat is de voornaam en achternaam van de ondertekenaar van Opdrachtnemer?
                'answer': 'James Bond'
            },
            {
                'questionId': 1346,
                # Wat is de voornaam en achternaam van de ondertekenaar van Opdrachtgever?
                'answer': 'John Doe'
            },
            {
                'questionId': 1374,
                # Wat voor een product of dienst levert de Opdrachtnemer (Verwerker) of gaat deze leveren?
                'answer': 'Nothing'
            },
            {
                'questionId': 2331,
                # Wat is het huisnummer? (Opdrachtgever)
                'answer': '272'
            },
            {
                'questionId': 2332,
                # Wat is het huisnummer? (Opdrachtnemer)
                'answer': '1'
            },
            {
                'questionId': 2350,
                # Rechtbank bij u in de buurt.
                'answer': 'Rechtbank Oost-Brabant'
            }
        ]
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

    response = sign_contract(token, contract_id)
    assert response.status_code == http.HTTPStatus.OK

    response = requests.get(
        contract_url + f'/{contract_id}/download',
        headers=authorize | accept_pdf | {'pragma': 'no-cache', 'cache-control': 'no-cache'}
    )

    Path('./out').mkdir(parents=True, exist_ok=True)
    with open('./out/contract.pdf', 'wb') as file:
        file.write(response.content)

    return get_contract(token, contract_id).json()['parties'][1]['link']


if __name__ == '__main__':
    response = resource_owner_password_credentials_grant()
    response = get_api_client(response.json()['access_token'])

    # The previous steps do not need to be taken when copying the `client_id` and `client_secret` from the dashboard.
    response = client_credentials_grant(response.json()['client_id'], response.json()['client_secret'])
    access_token = response.json()['access_token']
    print(f'Access token: {access_token}')

    # Create a contract and fill in the necessary data.
    invite_link = create_contract(access_token, 107)

    print(f'http://localhost:8000/ondertekenen/{invite_link}')

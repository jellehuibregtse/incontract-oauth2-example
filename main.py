import os

import requests
from requests import Response

token_url = 'http://localhost:5000/oauth/token'
client_url = 'http://localhost:5000/oauth/client'


def resource_owner_password_credentials_grant() -> Response:
    data = {
        'grant_type': 'password',
        'client_id': 'website',
        'username': 'info@incontract.nl',
        'password': os.environ['PASSWORD'],
        'scope': 'user:read user:write contract:write contract:read'
    }

    return requests.post(
        token_url,
        data=data,
        verify=False,
        allow_redirects=False
    )


def get_api_client(token: str) -> Response:
    headers = {'Authorization': f'Bearer {token}'}
    return requests.get(client_url, headers=headers)


def client_credentials_grant(client_id: str, client_secret: str) -> Response:
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
        'scope': 'user:read user:write contract:write contract:read'
    }

    return requests.post(
        token_url,
        data=data,
    )


if __name__ == '__main__':
    response = resource_owner_password_credentials_grant()
    response = get_api_client(response.json()['access_token'])

    # The previous steps do not need to be taken when copying the `client_id` and `client_secret` from the dashboard.
    response = client_credentials_grant(response.json()['client_id'], response.json()['client_secret'])
    access_token = response.json()['access_token']
    print('Access token:', access_token)

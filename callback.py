from bottle import post, request, run

from main import get_access_token, download_contract


@post('/callback')
def callback():
    print(f'Callback: {request.json}')
    access_token = get_access_token()
    contract_id = request.json['contract_id']
    download_contract(access_token, contract_id)


if __name__ == '__main__':
    # Run bottle webserver for callback.
    run(host='localhost', port=8080)

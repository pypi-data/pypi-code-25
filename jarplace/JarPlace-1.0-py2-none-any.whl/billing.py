import requests
from main import auth


def show(args):
    token = auth.get_token()
    response = requests.get('https://repo.jar.place:3333/billing/list', headers={'Authorization': 'Bearer ' + token})
    print(response.text)


def plan(args):
    token = auth.get_token()
    response = requests.get('https://repo.jar.place:3333/billing', headers={'Authorization': 'Bearer ' + token})
    print(response.text)


def change(args):
    token = auth.get_token()
    response = requests.patch('https://repo.jar.place:3333/billing/%s' % args.name,
                              headers={'Authorization': 'Bearer ' + token})
    print(response.text)

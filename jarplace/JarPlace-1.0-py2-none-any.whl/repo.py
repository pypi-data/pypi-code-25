import requests
import json
import pprint
from main import auth


def show(args):
    token = auth.get_token()
    response = requests.get('https://repo.jar.place:3333/owner',
                            headers={'Authorization': 'Bearer ' + token})
    try:
        print(json.loads(response.text)['repositories'])
    except json.JSONDecodeError:
        print(response.text)


def info(args):
    token = auth.get_token()
    response = requests.get('https://repo.jar.place:3333/repositories/%s' % args.name,
                            headers={'Authorization': 'Bearer ' + token})
    try:
        pprint.pprint(json.loads(response.text))
    except json.JSONDecodeError:
        print(response.text)


def create(args):
    token = auth.get_token()
    response = requests.put('https://repo.jar.place:3333/repositories',
                            headers={'Authorization': 'Bearer ' + token},
                            json={
                                'name': args.name,
                                'restricted': args.private
                            })
    try:
        pprint.pprint(json.loads(response.text))
    except json.JSONDecodeError:
        print(response.text)


def modify(args):
    token = auth.get_token()
    response = requests.patch('https://repo.jar.place:3333/repositories',
                              headers={'Authorization': 'Bearer ' + token},
                              json={
                                  'name': args.name,
                                  'restricted': args.private
                              })
    try:
        pprint.pprint(json.loads(response.text))
    except json.JSONDecodeError:
        print(response.text)


def delete(args):
    decision = input('It will erase all its content and you will not be able to reuse its name. '
                     'This operation is not reversible! \n'
                     'Are you sure you want to delete the \'%s\' repository? (y/N): ' % args.name)
    if decision is not 'y':
        return
    token = auth.get_token()
    response = requests.delete('https://repo.jar.place:3333/repositories/%s' % args.name,
                               headers={'Authorization': 'Bearer ' + token})
    print(response.text)

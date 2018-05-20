import requests


def search_avatar(user):
    """"
    Search the avatar of a user in Githbu

    :param user: str with name of Github user
    :return str with the link of avatar
    """

    url = f'https://api.github.com/users/{user}'
    resp = requests.get(url)
    return resp.json()['avatar_url']


if __name__ == '__main__':
    print(search_avatar('alvesgabriel'))

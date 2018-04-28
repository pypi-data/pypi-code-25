from bs4 import BeautifulSoup
import requests

URL = 'https://www.codewars.com/users/leaderboard'


class User:
    def __init__(self, name, clan, honor):
        self.name = name
        self.clan = clan
        self.honor = honor


class Leaderboard:
    def __init__(self, list_of_users):
        position = {}
        for counter, user in enumerate(list_of_users):
            position[counter+1] = user
        self.position = position


def solution():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    tr = soup.findChildren('tr')
    tr = iter(tr)
    next(tr)
    list_of_users = []
    for user in tr:
        name = user.find('td', {'class': 'is-big'}).find('a').contents[1]

        try:
            clan = user.find_all('td')[-2].contents[0]
        except IndexError:
            clan = ''

        honor = user.find_all('td')[-1].contents[0]

        current_user = User(name, clan, int(honor))

        list_of_users.append(current_user)

    leaderboard = Leaderboard(list_of_users)

    return leaderboard


def main():
    leaderboard = solution()
    for i in range(1, 501):
        print(f"{i}.{leaderboard.position[i].name}, "
              f"clan: {leaderboard.position[i].clan if leaderboard.position[i].clan else 'No clan'},"
              f" honor: {leaderboard.position[i].honor}")


if __name__ == '__main__':
    main()

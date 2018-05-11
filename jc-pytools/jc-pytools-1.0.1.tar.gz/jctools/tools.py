from os import system


def cls():
    completed = system('cls')
    if int(completed) == 0:
        return
    else:
        completed = system('clear')
        if int(completed) == 0:
            return
        else:
            print('\n' * 100)

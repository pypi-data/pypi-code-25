from termcolor import colored


def main():
    text, color = u'Hello, Simbirsoft!', 'blue'
    message = colored(text, color)
    print(message)


if __name__ == '__main__':

    main()

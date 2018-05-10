from random import randint

def give_apep(description):
    return "APEP#{}: {}".format(randint(10000, 99999), description)


if __name__ == "__main___":
    print(give_apep("Que Joaquín explique cómo funciona el sistema de id de las APEP."))
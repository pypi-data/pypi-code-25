import configparser

config = configparser.ConfigParser()

print("Configuração de acesso")

config['AUTH'] = {'Key': input("Informe a KEY: "),
        'Token': input("Informe o TOKEN: ")}

print("Configuração de board")

more="S"
board_list = []

while more=="S":
    board_id = input("Informe o ID do Board que você deseja: ")
    more = input("Deseja exportar outro board? (S/N): ").upper()
    board_list.append(board_id)

config['BOARDS'] = {"BoardList": board_list}

with open('config', 'w') as configfile:
    config.write(configfile)

exit("Ready to go")

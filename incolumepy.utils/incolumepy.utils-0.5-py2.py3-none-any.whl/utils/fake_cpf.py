from rstr import rstr
from string import digits

def gen_fake_cpf(formated=True):
    '''
    Cria um Gerador numeros de CPF com 11 digitos nao verificados
    :param formated: True para formatados e False para somente numeros
    :return: string com numero de CPF
    '''
    while True:
        cpf = rstr(digits, 11)
        if formated:
            yield "{}.{}.{}-{}".format(cpf[:3], cpf[3:6], cpf[6:9], cpf[-2:])
        else:
            yield cpf

if __name__ == '__main__':
    c1 = gen_fake_cpf()
    c2 = gen_fake_cpf(False)
    print([next(c1) for x in range(5)])
    print([next(c2) for x in range(5)])

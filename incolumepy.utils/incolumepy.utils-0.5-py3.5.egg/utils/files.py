import os

def realfilename(filebase, ext=None, digits=2, separador=True):
    count = 0
    sufix = {'default': 'txt', 0: 'txt', 1: None, 2: None}

    if len(filebase.split('.')) > 1:
        prefix = os.path.abspath(os.path.dirname(filebase))
        basename = os.path.basename(filebase)
        #print('1: ', prefix, basename)

        filebase, sufix[1] = basename.split('.')
        #print('2: ', filebase, sufix[1])

        filebase = '{}/{}'.format(prefix, filebase)
        #print(filebase, sufix[1])

    if ext:
        sufix[2] = ''.join([i for i in ext if i.isalpha()])
        ext = sufix[2]
    elif sufix[1]:
        ext = sufix[1]
    else:
        ext = sufix['default']

    dir = os.path.dirname(filebase)
    print(dir)
    os.makedirs(os.path.abspath(dir), exist_ok=True, mode=0o777)
    if separador:
        sep = '_'
    else:
        sep = ''
    while True:
        try:
            if count <= 0:
                filename = '{}.{}'.format(filebase, ext)
            else:
                filename = ('{}{}{:0>%s}.{}' % digits).format(filebase, sep, count, ext)
            if os.path.isfile(filename): raise IOError('Arquivo existente: {}'.format(filename))
            print('Criado arquivo: {}'.format(filename))
            return filename
        except IOError as e:
            print(e)
        except:
            raise
        finally:
            count += 1

if __name__ == '__main__':
    with open(realfilename(
            os.path.join('tmp', 'britodfbr','diretorio', 'para', 'teste'),
            ext='.dat', separador=True), 'w') as file:
        file.write('teste ok')

    with open(realfilename(
            os.path.join('tmp', 'diretorio', 'para', 'teste'),
            separador=True, ext='md'),'w') as file:
        file.write('teste ok')

    with open(realfilename(('tmp/teste/test.json'),
            separador=True, ext='bash'),'w') as file:
        file.write('teste ok')

    with open(realfilename(('tmp/teste/lll'),
            separador=True),'w') as file:
        file.write('teste ok')

    with open(realfilename(('tmp/teste/jjj.json'),
            separador=True),'w') as file:
        file.write('teste ok')

    with open(realfilename(os.path.join('tmp', os.path.basename(__file__)),
            digits=4, ext='log', separador=False), 'a') as file:
        file.write(file.name)

    with open(realfilename(os.path.join('tmp', os.path.basename(__file__)),
            digits=5, ext='log', separador=True), 'a') as file:
        file.write(file.name)

    with open(realfilename(os.path.join('tmp', os.path.basename(__file__)),
            digits=5, ext='log'), 'a') as file:
        file.write(file.name)

    with open(realfilename('../utils/tmp/registro.xml'), 'w') as file:
        file.write(file.name)
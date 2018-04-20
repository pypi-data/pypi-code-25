import os

def mkdirs(dirs):
    """ mkdirs(dirs)

    crea un directorio a partir del nombre dado

    @param dirs: el nombre del directorio a crear
    """
    if not os.path.exists(dirs):
        os.makedirs(dirs)

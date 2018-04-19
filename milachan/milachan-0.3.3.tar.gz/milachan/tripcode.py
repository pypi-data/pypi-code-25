import crypt

def tripcode(clave):
    clave = clave[:8]
    salt = clave[1:3]
    return crypt.crypt(clave, salt)[-10:]


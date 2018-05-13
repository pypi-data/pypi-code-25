import uuid


def newguid(upper: bool = True):
    """
    Generate and return a new, pseudo-random, UUID / GUID as str.
    :return: str
    """

    guid = str(uuid.uuid4())
    if upper:
        return guid.upper()
    else:
        return guid

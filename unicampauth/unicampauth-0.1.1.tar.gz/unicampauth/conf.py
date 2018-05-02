from . import settings as local_settings


def import_class(cl):
    d = cl.rfind(".")
    classname = cl[d + 1:len(cl)]
    m = __import__(cl[0:d], globals(), locals(), [classname])
    return getattr(m, classname)


class Settings():

    def __getattr__(self, name):
        attr = getattr(local_settings, name)
        if name.endswith('_CLASS'):
            attr = import_class(attr)
        return attr


settings = Settings()

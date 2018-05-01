import importlib
from .settings import *


def upload_file(file):
    service_provider = get_service_provider_class()(file['path'], file['order'])
    link = service_provider.upload_file()

    service_provider.progressbar.finish(link)

    return link


def get_service_provider_class():
    return getattr(importlib.import_module('pytransfer.services'), default_provider['class'])

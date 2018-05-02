# -*- coding: utf-8 -*-
import sys
import os
import logging
import os.path

logger = logging.getLogger(__name__)


def import_path(filename):
    module = None
    directory, module_name = os.path.split(filename)
    module_name = os.path.splitext(module_name)[0]
    path = list(sys.path)
    sys.path.insert(0, directory)
    try:
        module = __import__(module_name)
    except Exception:
        logger.exception('An exception occurred', exc_info=sys.exc_info())
    finally:
        sys.path[:] = path  # restore
    return module


def load_checker():
    checker_module_name = os.getenv(
        'THEMIS_FINALS_CHECKER_MODULE',
        os.path.join(os.getcwd(), 'checker.py')
    )
    checker_module = import_path(checker_module_name)
    checker_push = getattr(checker_module, 'push')
    checker_pull = getattr(checker_module, 'pull')
    return checker_push, checker_pull

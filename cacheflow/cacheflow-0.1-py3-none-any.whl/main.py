import logging
import sys

from .base import NullCache
from .builtin_modules import BuiltinModulesLoader
from .executor import Executor
from .json import load_workflow
from .python import BuiltinPythonLoader


def main():
    """Entrypoint for the ``cacheflow`` command.
    """
    logging.basicConfig(level=logging.INFO)

    with open(sys.argv[1]) as fp:
        workflow = load_workflow(fp)

    executor = Executor(NullCache(),
                        [BuiltinPythonLoader(), BuiltinModulesLoader()])
    executor.execute(workflow)

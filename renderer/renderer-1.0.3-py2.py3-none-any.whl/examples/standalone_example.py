# coding=utf-8
import json

import sys

from renderer.bridge_context import Context
from iohandler import IOFile

fph = IOFile.IOFileHandler()

fileHandler = IOFile.IOFileHandler()


def open_json_file(file_name, file_path):
    with \
            fileHandler.open(file_name=file_name, file_path=file_path, create_file_if_none=False,
                             create_package=False, mode='r') as file_reader:
        raw_obj = fileHandler.read(reader=file_reader)
    x = json.loads(raw_obj)
    return x


def _standalone_implemetation(file_name, file_path):
    x = open_json_file(file_name, file_path)
    context = Context()
    targets = ['code', 'stdout', 'db', 'file']
    target_writers = dict()
    with fileHandler.open(
            file_name='db.log',
            file_path=file_path,
            create_file_if_none=True,
            create_package=False, mode='ab+'
    )as db, fileHandler.open(
        file_name='file.log',
        file_path=file_path,
        create_file_if_none=True,
        create_package=False, mode='ab+'
    ) as fl:
        target_writers['db'] = db
        target_writers['file'] = fl
        for target in targets:
            result = context.render(x, target=target)
            print("Target:{tgt} || Result Type:{ty}\n".format(tgt=target.capitalize(),
                                                              ty=type(result)))
            print(result)
            print("\n\n")
            if target in ['db', 'file']:
                fileHandler.write(target_writers[target], data=result)
            else:
                pass


def main():
    _standalone_implemetation(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()

import os
from shutil import copyfile
import argparse
import colorama
from colorama import Fore


def command_args():
    parser = argparse.ArgumentParser(description='pyRecoverName')
    parser.add_argument('-p', dest='root', type=str, help='misencoded path')
    parser.add_argument('-r', dest='recover', type=str, help='recover path')
    parser.add_argument('-s', dest='source', type=str, help='source encoding, default gb18030')
    parser.add_argument('-t', dest='target', type=str, help='target encoding, default utf8')
    parser.set_defaults(root=None, recover=None, source="gb18030", target="utf8")
    args = parser.parse_args()
    return args


def main():
    colorama.init(autoreset=True)
    args = command_args()
    root_path = args.root
    recover_path = args.recover
    source_encoding = args.source
    target_encoding= args.target
    if root_path is None:
        raise ValueError
    if recover_path is None:
        raise ValueError
    for current_path, dirs, files in os.walk(root_path, False):
        if current_path.index(root_path) != 0:
            raise ValueError
        trunk_path = current_path[len(root_path)+1:]
        try:
            fixed_path = trunk_path.encode(source_encoding, "replace").decode(target_encoding)
            print(Fore.GREEN + 'fixed pathname encoding {}->{}'.format(trunk_path, fixed_path))
            trunk_path = fixed_path
        except Exception as e:
            if trunk_path.encode(target_encoding).decode(target_encoding) != trunk_path:
                raise e
            print("don't change pathname encoding {}".format(trunk_path))
        new_path = os.path.join(recover_path, trunk_path)
        os.makedirs(new_path, exist_ok=True)
        for file in files:
            try:
                fixed_file = file.encode(source_encoding, "replace").decode(target_encoding)
                print(Fore.GREEN + 'fixed filename encoding {}->{}'.format(file, fixed_file))
                new_file = fixed_file
            except Exception as e:
                if file.encode(target_encoding).decode(target_encoding) == file:
                    print("don't change filename encoding {}".format(file))
                    new_file = file
                else:
                    raise e
            old_path = os.path.join(current_path, file)
            target_path = os.path.join(new_path, new_file)
            copyfile(old_path, target_path)


if __name__ == '__main__':
    main()

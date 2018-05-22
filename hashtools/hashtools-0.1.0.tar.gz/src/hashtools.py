import os
import sys
import hashlib
import click


def get_algorithms_available():
    if hasattr(hashlib, "algorithms_available"):
        methods = list(hashlib.algorithms_available)
        methods.sort()
        return methods
    else:
        return ["md5", "sha1", "sha224", "sha256", "sha384", "sha512"]


def get_hash_method(script):
    script = os.path.realpath(script)
    _, filename = os.path.split(script)
    name, _ = os.path.splitext(filename)
    return name


def get_file_hash(hash_method_name, file):
    buffer_size = 1024 * 64
    close_file_flag = False
    if file == "-":
        fileobj = sys.stdin.buffer
    else:
        fileobj = open(file, "rb")
        close_file_flag = True
    try:
        gen = hashlib.new(hash_method_name)
        while True:
            buffer = fileobj.read(buffer_size)
            if not buffer:
                break
            gen.update(buffer)
        return gen.hexdigest()
    finally:
        if close_file_flag:
            fileobj.close()


def print_hash_code(code, file, verbose):
    if not verbose:
        click.echo(code)
    else:
        click.echo("{code} {file}".format(code=code, file=file))

@click.command()
@click.option("-v", "--verbose", is_flag=True)
@click.argument("files", nargs=-1)
@click.pass_context
def make_hash(context, verbose, files):
    hash_method_name = context.obj["hash_method_name"]
    if not files:
        files = ["-"]
    for file in files:
        code = get_file_hash(hash_method_name, file)
        print_hash_code(code, file, verbose)


def main():
    hash_method_name = get_hash_method(sys.argv[0])
    if not hash_method_name in get_algorithms_available():
        hash_method_name = "md5"
    make_hash(obj={"hash_method_name": hash_method_name})

if __name__ == "__main__":
    main()

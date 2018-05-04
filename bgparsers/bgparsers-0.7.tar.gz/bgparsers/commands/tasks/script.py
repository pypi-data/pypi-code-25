from bgparsers import readers
from subprocess import Popen, PIPE

HEADERS = ["SAMPLE", "DONOR", "CHROMOSOME", "POSITION", "REF", "ALT", "STRAND", "ALT_TYPE"]


def __skip(row, where):
    # TODO Implement where using annotations

    if where is None:
        return False

    for k, v in where.items():
        if str(row.get(k, None)) != v:
            return True
    return False


def run(selection, script=None):
    group_key, group_values = selection

    process = Popen(script, shell=True, stdin=PIPE, stdout=PIPE, env={"GROUP_KEY": 'None' if group_key is None else group_key})
    try:
        for r in readers.variants(group_values):
            process.stdin.write("{}\n".format("\t".join([str(r.get(h, "")) for h in HEADERS])).encode())
            process.stdin.flush()
        process.stdin.close()
    except BrokenPipeError:
        pass

    output = []
    try:
        while True:
            out = process.stdout.readline().decode().strip()
            if out == "":
                break
            output.append(out)
        process.stdout.close()
    except BrokenPipeError:
        pass

    return group_key, output



from pathlib import Path
from itertools import groupby


def program(line):
    return line.split()[0]


def number_of_calls(prog_lines):
    return len(list(prog_lines[1]))


def take(n, iter):
    for _, e in zip(range(n), iter):
        yield e


def main():
    bash_history = Path.home() / '.bash_history'
    lines = bash_history.read_text().split('\n')
    non_empty_lines = sorted(l.strip() for l in lines if l.strip())
    lines_by_program = [(program, list(lines))
                        for program, lines in groupby(non_empty_lines, program)]

    for prog, lines in sorted(lines_by_program, key=number_of_calls):
        print(prog)
        for line in take(3, set(lines)):
            print(f'    {line}')


if __name__ == '__main__':
    main()

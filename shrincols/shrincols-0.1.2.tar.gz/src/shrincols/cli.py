import sys
import os.path
import argparse
import re

def shrink_cols(text, cols):
    """
    shrinks a text for fit in `cols` columns
    """
    if len(text) <= cols:
        return text
    if re.sub("\s+", "", text) == "":
        return "\n"
    i = 1
    j = 1
    shrinked = text
    while True:
        if  j > 1 and (j-1) % cols == 0:
            while shrinked[i] != ' ' and i > 0:
                i -= 1
            shrinked = shrinked[:i] + '\n' + shrinked[i+1:]
            j = 1
            continue
        j += 1
        i += 1
        if i == len(shrinked):
            break
    return shrinked

def justify(text, cols):
    """
    Justify the text for achieving a number of cols
    """
    if not re.match(".*\w.*", text):
        return text

    lines = text.split('\n')

    for l, line in enumerate(lines):
        if not re.match(".*\w.*", line):
            continue

        spaces_max  = len([c for c in line if c == ' '])
        i           = 1
        spaces_from = " "
        spaces_to   = "  "

        while len(line) < cols:
            while i <= spaces_max:
                justy = line.replace(spaces_from, spaces_to, i)
                if len(justy) == cols:
                    break
                i += 1

            line         = line.replace(spaces_from, spaces_to, i)
            spaces_from += " "
            spaces_to   += " "
            i            = 1

        lines[l] = line

    return '\n'.join(lines)

class InputAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        input_string = values[0]
        
        # if it is a string
        if len(input_string.split(' ')) > 1:
            namespace.string = input_string
            namespace.filename = None
        else:
            namespace.string = None
            namespace.filename = input_string
            if not os.path.exists(input_string):
                parser.error("File does not exist!")

def create_parser():
    parser = argparse.ArgumentParser(description="""
    Shrinks an input text or valid text file to match a specified
    number of columns (default is 80).
    """)
    parser.add_argument('input', type=str,
        help='The input string or filename',
        metavar=("INPUT_STRING"),
        nargs=1,
        action=InputAction,
        default=sys.stdin)
    parser.add_argument('--cols', '-c', type=int,
        help='Max number of columns')
    parser.add_argument('--justify', '-j',
        help='Justify the text', action='store_true')
    parser.add_argument('--output', '-o',
        help='File output')
    return parser

def manager(args):
    """
    This function receives the args and control the whole stuff
    checkign whether the input is a string or a filename
    if the number columns is given, and checking whether the 
    text must be justified
    """
    cols = args.cols or 80
    result = ''
    if args.filename:
        with open(args.filename, 'r') as f:
            lines = f.readlines()
            lines = [shrink_cols(l, cols) for l in lines]
            if args.justify:
                lines = [justify(l, cols) for l in lines]
            result = ''.join(lines)
    else:
        result = shrink_cols(args.string, cols)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(result)
    return result

def main():
    """
    entry point for setup tools
    """
    parser = create_parser()
    if not sys.stdin.isatty():
        input_string = sys.stdin.read()
        args = parser.parse_args([input_string] + sys.argv[1:])
    else:
        args = parser.parse_args()
    print(manager(args))
    
if __name__ == '__main__':
    main()

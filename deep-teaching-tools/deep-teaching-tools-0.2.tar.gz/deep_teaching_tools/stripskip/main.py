from argparse import ArgumentParser

import nbformat


DESCRIPTION = 'Strip all cells marked as slide_type skip from a Jupyter notebook.'


def main():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        'input_file', action='store', type=str, metavar='INPUT_FILE',
        help='Read Jupyter notebook from INPUT_FILE path to remove skip cells. This will not alter the INPUT_FILE.'
    )
    parser.add_argument(
        'output_file', action='store', type=str, metavar='OUTPUT_FILE',
        help='Write Jupyter notebook without skip cells to OUTPUT_FILE path.'
    )
    args = parser.parse_args()

    with open(args.input_file) as f:
        nb = nbformat.read(f, as_version=nbformat.NO_CONVERT)

    i = 0
    while i < len(nb.cells):
        cell = nb.cells[i]
        remove = False

        try:
            if 'skip' in cell.metadata.slideshow.slide_type:
                remove = True
        except AttributeError:
            pass

        if remove:
            nb.cells.pop(i)
        else:
            i += 1

    with open(args.output_file, 'w') as f:
        nbformat.write(nb, f)

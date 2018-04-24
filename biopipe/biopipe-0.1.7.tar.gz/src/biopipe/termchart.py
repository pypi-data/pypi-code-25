# -*- coding: utf-8 -*-
from __future__ import print_function

import subprocess

# Define block characters.
FULL_BLOCK = u'\u2588'
BLOCK_CHARACTERS = ['', u'\u258F', u'\u258E', u'\u258D', u'\u258C', u'\u258B', u'\u258A', u'\u2589', FULL_BLOCK]


def get_terminal_width():
    """Return the width of current open terminal."""
    return int(subprocess.check_output(['stty', 'size']).split()[1])


def bar(length):
    """Return a string of bar with given length (approximately).
    """
    integer, decimal = int(length), length - int(length)
    bar_fragments = [FULL_BLOCK for _ in range(integer)]

    decimal = min(1, decimal + 1/16)  # Right-truncate to 1.
    bar_fragments.append(BLOCK_CHARACTERS[int(8 * decimal)])
    return ''.join(bar_fragments)


def get_layout(data, width_limit):
    """A row of a chart can be dissected as four components below:

    1. Label region ('label1'): fixed length (set to max label length + 1)
    2. Intermediate region (' | '): 3 characters
    3. Bar region ('▇ or '): variable length

    This function first calculates the width of label region(1),
    and compute the longest of the lengths of bar(3) regions.
    Then returns the layout of the chart, which is described by the widths of
    each regions.

    The total widths of the chart will not exceed width_limit-15 characters, just for an
    aesthetic reason.
    """
    labels = [d[0] for d in data]
    label_width = len(max(labels, key=lambda label: len(label))) + 1
    intermediate_width = 3
    bar_width = (width_limit - 15) - (label_width + intermediate_width)

    return label_width, bar_width


def terminal_bar_chart(data, title=None, sort=False, width_limit=180):
    """Print bar chart to the terminal.
    Data should be formatted like:

    [
        (label1, value1),
        (label2, value2),
        (label3, value3),
    ]

    Then the data will be printed out as below:

                Title (optional)

        -----------------------------------
        label1 | ▇▇▇▇▇▇▇▇▇▇ value1
        label2 | ▇▇▇▇ value2
        label3 | ▇▇▇▇▇▇▇ value3
        label4 | ▇▇ value4

    if sort=True, values will be sorted in *descending* order.
    Basically this funtion assumes wide terminal so that
    the chart can have width of exactly 120 characters.
    """
    width = get_terminal_width()
    assert width > width_limit, "Terminal is too narrow to print out the chart!"

    values = [d[1] for d in data]

    label_width, bar_width = get_layout(data, width_limit=width_limit)
    bar_normalizer = bar_width / max(values)

    print()
    print()
    if title is not None:
        print(title.center(width_limit))
    else:
        print('Bar chart'.center(width_limit))
    print('-' * width_limit)

    if sorted:
        data.sort(key=lambda x: x[1], reverse=True)

    for label, value in data:
        normalized_length = value * bar_normalizer
        print(label.rjust(label_width), end='')
        print(' | ', end='')
        print(bar(normalized_length), round(value, 2))
    print()
    print()

"""This is "The Simple Tree Lib".
The Simple Tree Lib" provides Tree and Node structures and just one alg
DFS traversal.
Cause this all was done just for as a test work for the job application.

This script takes a file with a tree data and outputs all ways in this tree.
Files cat be a .dot file or a simple text file, with lines like this:
A->B;
B->C;
Where A,B and C are Nodes in an input tree and A->B indicates that
there is an edge from A to B.

Usage:
    waysintree <file_name> [ --delimiter DELIMETER ]

Options:
  -h --help     show this help message and exit
  --delimiter   delimiter between nodes in a way

"""

from .structures import Node, Tree
from .algths import df_traversal
from .halperfuncs import load_tree, save_tree, way_to_str

__all__ = ['Node', 'Tree', 'df_traversal',
            'load_tree', 'save_tree', 'way_to_str']

from docopt import docopt
from .halperfuncs import way_to_str

def main():
    args = docopt(__doc__)

    tree = load_tree(args['<file_name>'])
    ways = df_traversal(tree)
    print("\n".join([ way_to_str(way,
                delimiter = ['', args['DELIMETER']][args['--delimiter']])
                for way in ways ]))

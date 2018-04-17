import contextlib
import pathlib

from .nucamino import Nucamino


def align(seqs=None, profile=None, genes=None, check=True):
    '''Align a fasta-formatted collection of nucleotide sequences using
    the given profile name and iterable of gene names

    See :class:`Nucamino` for details about the arguments.
    '''
    alignment = Nucamino(
        seqs=seqs,
        profile=profile,
        genes=genes,
        check=check,
    )
    return alignment.result


def align_file(input_file, profile=None, genes=None, check=True):
    '''Align a fasta-formatted file of input sequences using the given
    profile name and iterable of gene names.

    :param:`input_file` can be a file object, a `string`, or a
    `pathlib.Path`. Its contents will be passed to :class:`Nucamino`.
    If it's a file, it will be closed.

    See :class:`Nucamino` for details about the other arguments.
    '''
    if isinstance(input_file, str) or isinstance(input_file, pathlib.Path):
        input_file = open(input_file, 'r')
    with contextlib.closing(input_file) as inf:
        seqs = inf.read()
    return align(seqs=seqs, profile=profile, genes=genes, check=check)

import functools
import json
import subprocess


class Nucamino(object):

    @classmethod
    def _nucalign(cls, inputseqs, profile, genes, check=True):
        gene = ",".join(g.upper() for g in genes)
        command = ["./nucamino", "align", profile, gene, "-q", "-f", "json"]
        if type(inputseqs) is not bytes:
            inputseqs = bytes(inputseqs, 'utf8')
        align_proc = subprocess.run(
            command,
            input=inputseqs,
            stdout=subprocess.PIPE,
        )
        if check:
            align_proc.check_returncode()
        outp = align_proc.stdout.decode('utf8')
        return json.loads(outp), align_proc

    def __init__(self, seqs, profile, genes, check=True):
        '''Align a FASTA-formatted collection of nucleotide sequences and
        return the results.

        :param:`seq` is a FASTA-formatted collection of nucleotide
        sequences to align.

        :param:`profile` is the name of a built-in nucamino alignment
        (which specifies the reference sequence and scoring parameters
        used by the aligner). See :func:`profiles` for info on how to
        get a list of available profiles.

        :param:`genes` is an iterable of gene names to include in the
        alignment. See :func:`profile_genes` for details on how to get
        a list of available genes for each profile.

        :param:`check` Indicates that the return-code of the alignment
        process should be checked, and an exception raised if it's an
        error code. The default is `True`.
        '''
        self._check_profile(profile)
        self.result, self.proc = self._nucalign(
            seqs,
            genes=genes,
            profile=profile,
            check=check,
        )

    # `profiles` and `profile_genes` could almost be constants, but to
    # track changes in the underlying nucamino binary, instead we
    # interrogate the binary the first time they're accessed and cache
    # the result.

    @staticmethod
    @functools.lru_cache(maxsize=1)
    def profiles():
        '''Returns a list of supported alignment profiles'''
        command = ["./nucamino", "profile", "list"]
        proc = subprocess.run(command, stdout=subprocess.PIPE)
        proc.check_returncode()
        outp = proc.stdout.decode('utf8')
        return [
            profile.strip()
            for profile in outp.split('\n')
            if profile.strip()
        ]

    @classmethod
    @functools.lru_cache(maxsize=1)
    def profile_genes(cls, profile):
        cls._check_profile(profile)
        command = ["./nucamino", "profile", "list-genes", profile]
        proc = subprocess.run(command, stdout=subprocess.PIPE)
        proc.check_returncode()
        outp = proc.stdout.decode('utf8')
        return [
            gene.strip()
            for gene in outp.split()
            if gene.strip()
        ]

    @classmethod
    def _check_profile(cls, profile):
        if profile not in cls.profiles():
            raise ValueError("Unknown profile '{}'".format(profile))

import logging
import os, sys
import subprocess

from Bio.Alphabet import generic_dna
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
import click
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# click initialization
CONTEXT_SETTINGS = dict(help_option_names=['-h','--help'], max_content_width=90)

@click.group(context_settings= CONTEXT_SETTINGS)
@click.version_option(version='1.1.2')
def breseq_wrapper():
    pass

def merge_genbanks(output, *args):
    """merge a list of genebank files into the a file given by the first named argument.

    Args:
        merged_genbank (str): The first parameter is the name of the merged genbank output.
        *args: Variable length list of genbank files.

    Returns:
        file: genbank format
    """
    reformatted_genbank = args[0]
    gbk_list = args[1:]
    fhout = open(reformatted_genbank, 'w')
    sys.stderr.write("Loading %s\n" % reformatted_genbank)
    combined_record = SeqIO.read(reformatted_genbank, "genbank")

    print reformatted_genbank
    print gbk_list
    print args
    # FIXME This function was working but I modified the input feed <SPG>
    # fhout = open(first_gb, 'w')
    # firstGbk = args[1]
    # inputGbk = args[2:]
    # print inputGbk
    # sys.stderr.write("Loading %s\n" % firstGbk)
    # combined_record = SeqIO.read(firstGbk, "genbank")
    # # Forcing DNA alphabet in case of improper input files
    # combined_record.seq.alphabet = generic_dna
    # for filename in inputGbk:
    #     sys.stderr.write("Loading %s\n" % filename)
    #     record = SeqIO.read(filename, "genbank")
    #     record.seq.alphabet = generic_dna
    #     combined_record = combined_record + ("N" * 50) + record
    # sys.stderr.write("Merging into one record\n")
    # SeqIO.write(combined_record, fhout, "genbank")

def reformat_genbank(args):
    """Reformat genebank using biopython
    Currently adds numeric suffix to the end of the qualifiers "gene" and "dnas_title"

    Args:
        positional merged_genbank (str): The first parameter is the name of the merged genbank output.
        *args: Variable length list of genbank files.

    Returns:
        file: genbank format
    """
    gbk_list = args[0:]
    for filename in gbk_list:
        genbank_bname = filename[:filename.rfind('.g')]
        result = genbank_bname + '.reformatted.gb'
        fhout = open(result, 'w')
        sys.stderr.write("Loading %s\n" % filename)
        # changed read to parse:
        for record in SeqIO.parse(filename, "genbank"):
            # edited: record = SeqIO.read(filename, "genbank")
            # enforce DNA specification
            record.seq.alphabet = generic_dna
            # make a new record and append the original DNA seq
            new_record = SeqRecord(record.seq,
                       id=record.id,  # random accession number
                       name=record.name,
                       description=record.description)
            # iterate through the original features, append only non offending features
            rf = record.features
            # create a set of gene feature ids seen before
            gene_set = set()
            # keep track of 'gene' qualifier instance count
            gene_instnce_cnt = {}
            gene_locus = defaultdict(dict)
            for f in rf:
                # CDS and gene are allowed to share the same dnas_title?
                # asssume we allow only one instance of gene with given dnas_title, likewise for CDS
                type = f.type
                # check if feature = gene
                if type == 'gene':
                    # check if gene qualifier name has been seen before
                    if 'gene' in f.qualifiers:
                        gene = f.qualifiers['gene'][0]
                        if gene not in gene_set:
                            gene_set.add(gene)
                            new_record.features.append(f)
                            gene_instnce_cnt[gene] = 0
                        else:
                            gene = f.qualifiers['gene'][0]
                            gene_instnce_cnt[gene] = gene_instnce_cnt[gene] + 1
                            curnt_cnt = gene_instnce_cnt[gene]
                            gene = gene + '.%d' %curnt_cnt
                            f.qualifiers['gene'] = gene
                            # following check of dnas_title requires that gene qualifier exists for feat
                            if 'dnas_title' in f.qualifiers:
                                dnas_title = f.qualifiers['dnas_title'][0]
                                dnas_title = dnas_title + '.%d' % curnt_cnt
                                f.qualifiers['dnas_title'] = dnas_title
                            new_record.features.append(f)
                        gene = str(f.qualifiers['gene'][0])
                        gene_set.add(gene)
                        if not 'locus_tag' in f.qualifiers:
                            f.qualifiers.update({'locus_tag':gene})
                        locus_tag = str(f.qualifiers['locus_tag'][0])
                        gene_locus[locus_tag]['gene'] = gene
                        if not 'dnas_title' in f.qualifiers:
                            f.qualifiers.update({'dnas_title': gene})
                        dnas_title = f.qualifiers['dnas_title'][0]
                        gene_locus[locus_tag]['dnas_title'] = dnas_title
                if type == 'CDS':
                    # check if gene qualifier name has been seen before
                    if 'gene' in f.qualifiers:
                        gene = f.qualifiers['gene'][0]
                        if not gene in gene_set:
                            # the CDS feat sometimes has no matching gene
                            print 'hit CDS %s before gene, report error!' %gene
                            # sys.exit()
                        else:
                            if not 'locus_tag' in f.qualifiers:
                                f.qualifiers.update({'locus_tag': gene})
                            if not 'dnas_title' in f.qualifiers:
                                f.qualifiers.update({'dnas_title': gene})
                            locus_tag = f.qualifiers['locus_tag'][0]
                            fmt_gene = str(gene_locus[locus_tag]['gene'])
                            f.qualifiers['gene'] = fmt_gene
                            fmt_dna_tit = str(gene_locus[locus_tag]['dnas_title'])
                            f.qualifiers['dnas_title'] = fmt_dna_tit
                            new_record.features.append(f)
            SeqIO.write(new_record, fhout, "genbank")


if __name__ == '__main__':
    breseq_wrapper()
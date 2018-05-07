import argparse

from lib1.main import fold, blast, printdata, pic, get_id

def main(input, database, output, zeilen, view):
    fold(input)
    blast(database, input, output)
    printdata(output, zeilen)
    pic(view, get_id(input))


parser = argparse.ArgumentParser()
parser.add_argument('-input',
                    type=str,
                    default='input/sequence.fasta',
                    nargs='?',
                    help='Path to your local input file. RNA Sequence in FASTA format OR Sequence ONLY '
                         '(ATTN: FASTA format is required for unique file names!). Default: %(default)s')

parser.add_argument('-database',
                    type=str,
                    default='blastdb/nt.00',
                    nargs='?',
                    help='Path to your local NCBI database (ATTN: NCBI database format is required!).'
                         ' Default: %(default)s')

parser.add_argument('-output',
                    type=str,
                    default='output/blast.out',
                    nargs='?',
                    help='Name and location for BLAST data output. (ATTN: if no unique filename is chosen,'
                         ' this file will be overwritten) Default: %(default)s')

parser.add_argument('-zeilen',
                    type=str,
                    default='50',
                    nargs='?',
                    help='Number of BLAST lines in immediate shell output. Default: %(default)s')

parser.add_argument('-view',
                    type=str,
                    default='version',
                    nargs='?',
                    help='''2 available commands: version: RNA structure is saved in PostScript file color:
                    RNA structure is saved in PostScript file AND displayed in gv. 
                    e.g.: -view=color Default: %(default)s''')


'''Workaround: -version: Bild wird nicht angezeigt, nur gespeichert
               -color: Bild wird angezeigt, gv muss geschlossen werden um Code zu beenden'''


'''nargs = '?' Wichtig, damit wenn keine Eingabe erfolgt der Default Wert herangezogen wird'''


args = parser.parse_args()
dict_vars = vars(args)


'''vars is used to create a dictionary of argpars outputs, which then are used in the 'main' function'''


main(input=dict_vars['input'],
     database=dict_vars['database'],
     output=dict_vars['output'],
     zeilen=dict_vars['zeilen'],
     view="-"+dict_vars['view'])

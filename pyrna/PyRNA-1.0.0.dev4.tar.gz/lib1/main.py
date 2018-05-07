import subprocess


'''To perform shell scripts within Python, the subprocess module has to be imported'''


def fold(input):
    command_line = ['RNAfold', input]
    subprocess.run(command_line)
    return


'''The fold function executes the RNAfold tool (from ViennaRNAPackage 2.4.4)'''


def blast(database, input, output):
    command_line2 = ['blastn', '-db', database, '-query', input, '-out', output]
    subprocess.run(command_line2)
    return


'''The blast function executes the NCBI Blast search engine'''


def printdata(output, zeilen):
    command_line3 = ['head', '-n', zeilen, output]
    subprocess.run(command_line3)
    return


'''The printdata function creates an immediate Blast output, and lets you choose an outputfile for your Blast results'''


def pic(view, psinput):
    command_line4 = ['gv', view, psinput]
    subprocess.run(command_line4)
    return


'''The pic function lets you view your RNA secondary structure'''


def get_id(input):
    file = open(input, 'r')
    ifcon = file.read()
    if ifcon.startswith('>'):
        file = open(input, 'r')
        id = file.readline().split(" ")[0]
        psinput = (id.replace('>', '').replace(':', '_') + '_ss.ps')
    else:
        file = 'rna.ps'
        psinput = file
    return psinput


'''The get_id function differentiates between a fasta file format, or a pure sequence file 
(important for RNAfold output needed for the gv secondary view which generates a default rna.ps file)'''

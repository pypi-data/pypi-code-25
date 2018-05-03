import argparse
import glob
import pandas as pd
from Bio import SeqIO

def is_fasta(input_file):
    '''
    Function to Verify input_file is a FASTA file.
    '''
    with open(input_file, "r") as file:
        check_fasta = SeqIO.parse(file, 'fasta')
        return any(check_fasta)

def gc_content(input_file, output_file):
    '''
    Function for GC Content Calcution.
    '''
    
    # Check to see if input_file is FASTA
    if not is_fasta(input_file):
        raise ValueError('Input File must be FASTA')
    
    # Parse FASTA to collect each primer name and their DNA Seqs
    primers = []
    sequences = []
    for record in SeqIO.parse(input_file, 'fasta'):
        primers.append(record.description)
        sequences.append(record.seq)
        
    # Format primer name according to output requirements
    primers_format = []
    for primer in primers:
        desc = primer.split()
        if '_' in desc[0]:
            primers_format.append(desc[0])
        else:
            primers_format.append(desc[0] + '_' + desc[1])
    
    # Calculate GC content for each DNA seq
    gcPer = []
    for seq in sequences:
        gc_count = 0
        for base in seq.lower():
            if base == 'g' or base == 'c':
                gc_count += 1
            
        gcPer.append(round(gc_count / len(seq) * 100, 1))

    output_df = pd.DataFrame({'Primer': primers_format,
                              'GC Content(%)': gcPer})
    
    # Check if output_file already exists at given file path
    filesPresent = glob.glob(output_file)
    if not filesPresent:
        # Create CSV output file if not exists
        output_df.to_csv(output_file, columns=['Primer', 'GC Content(%)'])
        
    else:
        # Prompt user to enter different output_file 
        print('Warning: File Already Exists')
        output_new = input("Please Input New output_file:")
        output_df.to_csv(output_new, columns=['Primer', 'GC Content(%)'])

def main():
    
    # Use argparse for command-line arguments
    parser = argparse.ArgumentParser(     
                description="Calculating the GC Content(%) of each Sequence in a FASTA file",
                formatter_class=argparse.RawDescriptionHelpFormatter)
    
    parser.add_argument('--input_file', '-i',
                        help='File Path of Input Fasta File',
                        required=True)
    parser.add_argument('--output_file', '-o',
                        default='output.csv',
                        help='File Path of Output CSV File')

    args = parser.parse_args()
    
    # input_file is required, if none present raise exception
    if args.input_file == None:
        parser.print_help()
        raise ValueError('Must provide Input File Path')
        
    gc_content(**vars(args))
    
if __name__ == '__main__':
    main()
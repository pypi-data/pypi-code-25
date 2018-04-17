import sys
import logging

def run(args):
        if args.quanttype == 'IRI':
                from IRTools.quant_IRI import IRI_quant
                IRI_quanter = IRI_quant(args)
                IRI_quanter.quant()
                IRI_quanter.output_IRI_intron_level()
                IRI_quanter.output_IRI_gene_level()
                IRI_quanter.output_IRI_genome_wide()

        elif args.quanttype == 'IRC':
                from IRTools.quant_IRC import IRC_quant
                IRC_quanter = IRC_quant(args)
                IRC_quanter.quant()
                IRC_quanter.output_IRC_junction_level()
                IRC_quanter.output_IRC_intron_level()
                IRC_quanter.output_IRC_gene_level()
                IRC_quanter.output_IRC_genome_wide()
                
                












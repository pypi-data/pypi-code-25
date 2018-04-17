import sys
import os
import logging
import pkg_resources
import re
import pandas as pd
import subprocess
import collections
import copy
import networkx as nx
import HTSeq
from IRTools.quant_IRI import IRI_quant
from IRTools.quant_IRC import IRC_quant

class IRI_diff(object):
        def __init__(self, args):
                self.params = args.__dict__.copy()
                
                self.temp_dir = self.check_temp_dir(self.params['outdir']) 
                print("\tNote: Running \"IRTools diff\" will produce some intermediate files saved in directory: {}/".format(self.temp_dir))
                sys.stdout.flush()   
                
                self.logger = logging.getLogger()
        
        @staticmethod                        
        def check_temp_dir(outdir):
                temp_dir = os.path.join(outdir, "temp")
                if not os.path.exists( temp_dir ):
                        try:
                                os.makedirs( temp_dir ) 
                        except:
                                temp_dir = outdir
                                             
                return temp_dir                  
        
        def run_IRI_quant_for_all_samples(self, args):
                logging.info("Perform \"IRTools quant\" for all replciates from both samples")
                self.logger.disabled = True
                
                filtered_CIR_id_list = []
                
                s1files_list = self.params['s1files'].split(',')
                s2files_list = self.params['s2files'].split(',')                

                IRI_intron_level_df_s1_list = []
                IRI_intron_level_df_s2_list = []
                
                counts_s1_list = []
                counts_s2_list = []
                
                total_read_count_s1_list = []
                total_read_count_s2_list = []                
                
                IRI_quanter = IRI_quant(args)
                IRI_quanter.params['outdir'] = self.temp_dir 
                
                for i, s1file in enumerate(s1files_list):
                        IRI_quanter.params['name'] = self.params['name'] + "_S1_R%d" % (i+1)
                        IRI_quanter.params['altfile'] = s1file
                        
                        IRI_quanter.quant()
                        IRI_quanter.output_IRI_intron_level()
                        IRI_intron_level_df_s1_list.append(IRI_quanter.IRI_intron_level_df)
                        
                        counts_s1_list.append(copy.deepcopy(IRI_quanter.counts))
                        total_read_count_s1_list.append(IRI_quanter.total_read_count)
                        filtered_CIR_id_list.extend(IRI_quanter.filtered_CIR_id_list)
                                               
                for i, s2file in enumerate(s2files_list):
                        IRI_quanter.params['name'] = self.params['name'] + "_S2_R%d" % (i+1)
                        IRI_quanter.params['altfile'] = s2file
                        
                        IRI_quanter.quant()
                        IRI_quanter.output_IRI_intron_level()
                        IRI_intron_level_df_s2_list.append(IRI_quanter.IRI_intron_level_df)
                        
                        counts_s2_list.append(copy.deepcopy(IRI_quanter.counts))
                        total_read_count_s2_list.append(IRI_quanter.total_read_count)
                        filtered_CIR_id_list.extend(IRI_quanter.filtered_CIR_id_list)
                        
                filtered_CIR_id_list = list(set(filtered_CIR_id_list))
                
                for i, IRI_intron_level_df in enumerate(IRI_intron_level_df_s1_list):
                        IRI_intron_level_df_s1_list[i] = IRI_intron_level_df[IRI_intron_level_df.CIR_id.isin(filtered_CIR_id_list) == False]
                
                for i, IRI_intron_level_df in enumerate(IRI_intron_level_df_s2_list):
                        IRI_intron_level_df_s2_list[i] = IRI_intron_level_df[IRI_intron_level_df.CIR_id.isin(filtered_CIR_id_list) == False]                     
                        
                self.IRI_intron_level_data = {'s1_data': IRI_intron_level_df_s1_list,
                                              's2_data': IRI_intron_level_df_s2_list} 
                
                IRI_gene_level_df_s1_list = []
                IRI_gene_level_df_s2_list = []                
                
                for i, s1file in enumerate(s1files_list):
                        IRI_quanter.params['name'] = self.params['name'] + "_S1_R%d" % (i+1)
                        
                        IRI_quanter.counts = counts_s1_list[i]   
                        IRI_quanter.total_read_count = total_read_count_s1_list[i]
                        IRI_quanter.output_IRI_gene_level(filtered_CIR_id_list)
                        IRI_gene_level_df_s1_list.append(IRI_quanter.IRI_gene_level_df)
                
                        self.logger.disabled = False
                        logging.info("Sample: " + IRI_quanter.params['name'])                   
                        IRI_quanter.output_IRI_genome_wide()
                        self.logger.disabled = True
                        
                for i, s2file in enumerate(s2files_list):
                        IRI_quanter.params['name'] = self.params['name'] + "_S2_R%d" % (i+1)
                        
                        IRI_quanter.counts = counts_s2_list[i]
                        IRI_quanter.total_read_count = total_read_count_s2_list[i]
                        IRI_quanter.output_IRI_gene_level(filtered_CIR_id_list)
                        IRI_gene_level_df_s2_list.append(IRI_quanter.IRI_gene_level_df)
                
                        self.logger.disabled = False
                        logging.info("Sample: " + IRI_quanter.params['name'])  
                        sys.stdout.flush()
                        IRI_quanter.output_IRI_genome_wide()  
                        self.logger.disabled = True
                        
                self.IRI_gene_level_data = {'s1_data': IRI_gene_level_df_s1_list,
                                            's2_data': IRI_gene_level_df_s2_list}
                
                self.logger.disabled = False
        
        @staticmethod        
        def filter_invalid_rows(df):
                df['sum_IC_S1'] = df.apply(lambda row: sum([float(x) for x in row['IC_S1'].split(',')]), axis=1)
                df['sum_SC_S1'] = df.apply(lambda row: sum([float(x) for x in row['SC_S1'].split(',')]), axis=1)
                
                df['sum_IC_S2'] = df.apply(lambda row: sum([float(x) for x in row['IC_S2'].split(',')]), axis=1)
                df['sum_SC_S2'] = df.apply(lambda row: sum([float(x) for x in row['SC_S2'].split(',')]), axis=1)   
                
                df = df[(df['sum_IC_S1'] + df['sum_SC_S1'] > 0) & (df['sum_IC_S2'] + df['sum_SC_S2'] > 0) & ((df['sum_IC_S1']  != 0) | (df['sum_IC_S2'] != 0)) & ((df['sum_SC_S1']  != 0) | (df['sum_SC_S2'] != 0)) & (df['IncFormLen'] != 0) & (df['SkipFormLen'] != 0)]
                return df.drop(labels=['sum_IC_S1', 'sum_SC_S1', 'sum_IC_S2', 'sum_SC_S2'], axis=1)
                
        def generate_rmats_input_intron_level(self):
                logging.info("Generate inputs for rMATS for differential IR in intron level")
                
                rmats_input_intron_level_df = None
                
                for i, IRI_intron_level_df in enumerate(self.IRI_intron_level_data['s1_data']):
                        if rmats_input_intron_level_df is None:
                                rmats_input_intron_level_df = IRI_intron_level_df[((IRI_intron_level_df.intron_IRI >= 0) & (IRI_intron_level_df.intron_IRI <= 1)) | ((IRI_intron_level_df.adjacent_CER_read_count == 0) & (IRI_intron_level_df.CIR_read_count == 0))].loc[:,['CIR_id', 'CIR_length', 'adjacent_CER_length', 'CIR_read_count', 'adjacent_CER_read_count']]
                                rmats_input_intron_level_df['IncFormLen'] = rmats_input_intron_level_df['CIR_length'] + rmats_input_intron_level_df['adjacent_CER_length']
                                rmats_input_intron_level_df['SkipFormLen'] = rmats_input_intron_level_df['adjacent_CER_length']
                                rmats_input_intron_level_df['IC_S1_R%d' % (i+1)] = rmats_input_intron_level_df['CIR_read_count'] * rmats_input_intron_level_df['IncFormLen'] / (rmats_input_intron_level_df['IncFormLen'] - rmats_input_intron_level_df['SkipFormLen']) 
                                rmats_input_intron_level_df['SC_S1_R%d' % (i+1)] = rmats_input_intron_level_df['CIR_read_count'] + rmats_input_intron_level_df['adjacent_CER_read_count'] - rmats_input_intron_level_df['IC_S1_R%d' % (i+1)]
                                rmats_input_intron_level_df.drop(labels=['CIR_length', 'adjacent_CER_length', 'CIR_read_count', 'adjacent_CER_read_count'], axis=1, inplace=True)
                                
                        else:
                                rmats_input_intron_level_df = rmats_input_intron_level_df.merge(IRI_intron_level_df[((IRI_intron_level_df.intron_IRI >= 0) & (IRI_intron_level_df.intron_IRI <= 1)) | ((IRI_intron_level_df.adjacent_CER_read_count == 0) & (IRI_intron_level_df.CIR_read_count == 0))].loc[:,['CIR_id', 'CIR_read_count', 'adjacent_CER_read_count']], on='CIR_id')
                                rmats_input_intron_level_df['IC_S1_R%d' % (i+1)] = rmats_input_intron_level_df['CIR_read_count'] * rmats_input_intron_level_df['IncFormLen'] / (rmats_input_intron_level_df['IncFormLen'] - rmats_input_intron_level_df['SkipFormLen']) 
                                rmats_input_intron_level_df['SC_S1_R%d' % (i+1)] = rmats_input_intron_level_df['CIR_read_count'] + rmats_input_intron_level_df['adjacent_CER_read_count'] - rmats_input_intron_level_df['IC_S1_R%d' % (i+1)]
                                rmats_input_intron_level_df.drop(labels=['CIR_read_count', 'adjacent_CER_read_count'], axis=1, inplace=True)
                                
                for i, IRI_intron_level_df in enumerate(self.IRI_intron_level_data['s2_data']):
                        rmats_input_intron_level_df = rmats_input_intron_level_df.merge(IRI_intron_level_df[((IRI_intron_level_df.intron_IRI >= 0) & (IRI_intron_level_df.intron_IRI <= 1)) | ((IRI_intron_level_df.adjacent_CER_read_count == 0) & (IRI_intron_level_df.CIR_read_count == 0))].loc[:,['CIR_id', 'CIR_read_count', 'adjacent_CER_read_count']], on='CIR_id')
                        rmats_input_intron_level_df['IC_S2_R%d' % (i+1)] = rmats_input_intron_level_df['CIR_read_count'] * rmats_input_intron_level_df['IncFormLen'] / (rmats_input_intron_level_df['IncFormLen'] - rmats_input_intron_level_df['SkipFormLen']) 
                        rmats_input_intron_level_df['SC_S2_R%d' % (i+1)] = rmats_input_intron_level_df['CIR_read_count'] + rmats_input_intron_level_df['adjacent_CER_read_count'] - rmats_input_intron_level_df['IC_S2_R%d' % (i+1)]
                        rmats_input_intron_level_df.drop(labels=['CIR_read_count', 'adjacent_CER_read_count'], axis=1, inplace=True)
                        
                rmats_input_intron_level_df['IC_S1'] = rmats_input_intron_level_df.filter(regex=r'IC_S1').apply(lambda row: ','.join([str(item) for item in row.values]), axis=1)
                rmats_input_intron_level_df['SC_S1'] = rmats_input_intron_level_df.filter(regex=r'SC_S1').apply(lambda row: ','.join([str(item) for item in row.values]), axis=1)
                rmats_input_intron_level_df['IC_S2'] = rmats_input_intron_level_df.filter(regex=r'IC_S2').apply(lambda row: ','.join([str(item) for item in row.values]), axis=1)
                rmats_input_intron_level_df['SC_S2'] = rmats_input_intron_level_df.filter(regex=r'SC_S2').apply(lambda row: ','.join([str(item) for item in row.values]), axis=1)
                rmats_input_intron_level_df = rmats_input_intron_level_df.loc[:,['CIR_id', 'IC_S1', 'SC_S1', 'IC_S2', 'SC_S2', 'IncFormLen', 'SkipFormLen']] 
                
                rmats_input_intron_level_df = self.filter_invalid_rows(rmats_input_intron_level_df)
                
                rmats_input_intron_level_file = self.params['name'] + ".diff.rMATSinput.IRI.introns.txt" 
                self.rmats_input_intron_level_file_fullpath = os.path.join(self.temp_dir, rmats_input_intron_level_file)
                logging.info("Writing intron level rMATS inputs to file: {}".format(self.rmats_input_intron_level_file_fullpath))
                rmats_input_intron_level_df.to_csv(self.rmats_input_intron_level_file_fullpath, index=None, sep='\t', na_rep="NA") 
                        
        def generate_rmats_input_gene_level(self):
                logging.info("Generate inputs for rMATS for differential IR in gene level")
                
                rmats_input_gene_level_df = None
                
                for i, IRI_gene_level_df in enumerate(self.IRI_gene_level_data['s1_data']):
                        if rmats_input_gene_level_df is None:
                                rmats_input_gene_level_df = IRI_gene_level_df[((IRI_gene_level_df.gene_IRI >= 0) & (IRI_gene_level_df.gene_IRI <= 1)) | ((IRI_gene_level_df.gene_CER_read_count == 0) & (IRI_gene_level_df.gene_CIR_read_count == 0))].loc[:,['gene_id', 'gene_CIR_length', 'gene_CER_length', 'gene_CIR_read_count', 'gene_CER_read_count']]
                                rmats_input_gene_level_df['IncFormLen'] = rmats_input_gene_level_df['gene_CIR_length'] + rmats_input_gene_level_df['gene_CER_length']
                                rmats_input_gene_level_df['SkipFormLen'] = rmats_input_gene_level_df['gene_CER_length']
                                rmats_input_gene_level_df['IC_S1_R%d' % (i+1)] = rmats_input_gene_level_df['gene_CIR_read_count'] * rmats_input_gene_level_df['IncFormLen'] / (rmats_input_gene_level_df['IncFormLen'] - rmats_input_gene_level_df['SkipFormLen']) 
                                rmats_input_gene_level_df['SC_S1_R%d' % (i+1)] = rmats_input_gene_level_df['gene_CIR_read_count'] + rmats_input_gene_level_df['gene_CER_read_count'] - rmats_input_gene_level_df['IC_S1_R%d' % (i+1)]
                                rmats_input_gene_level_df.drop(labels=['gene_CIR_length', 'gene_CER_length', 'gene_CIR_read_count', 'gene_CER_read_count'], axis=1, inplace=True)
                                
                        else:
                                rmats_input_gene_level_df = rmats_input_gene_level_df.merge(IRI_gene_level_df[((IRI_gene_level_df.gene_IRI >= 0) & (IRI_gene_level_df.gene_IRI <= 1)) | ((IRI_gene_level_df.gene_CER_read_count == 0) & (IRI_gene_level_df.gene_CIR_read_count == 0))].loc[:,['gene_id', 'gene_CIR_read_count', 'gene_CER_read_count']], on='gene_id')
                                rmats_input_gene_level_df['IC_S1_R%d' % (i+1)] = rmats_input_gene_level_df['gene_CIR_read_count'] * rmats_input_gene_level_df['IncFormLen'] / (rmats_input_gene_level_df['IncFormLen'] - rmats_input_gene_level_df['SkipFormLen']) 
                                rmats_input_gene_level_df['SC_S1_R%d' % (i+1)] = rmats_input_gene_level_df['gene_CIR_read_count'] + rmats_input_gene_level_df['gene_CER_read_count'] - rmats_input_gene_level_df['IC_S1_R%d' % (i+1)]
                                rmats_input_gene_level_df.drop(labels=['gene_CIR_read_count', 'gene_CER_read_count'], axis=1, inplace=True)   
                                
                for i, IRI_gene_level_df in enumerate(self.IRI_gene_level_data['s2_data']):
                        rmats_input_gene_level_df = rmats_input_gene_level_df.merge(IRI_gene_level_df[((IRI_gene_level_df.gene_IRI >= 0) & (IRI_gene_level_df.gene_IRI <= 1)) | ((IRI_gene_level_df.gene_CER_read_count == 0) & (IRI_gene_level_df.gene_CIR_read_count == 0))].loc[:,['gene_id', 'gene_CIR_read_count', 'gene_CER_read_count']], on='gene_id')
                        rmats_input_gene_level_df['IC_S2_R%d' % (i+1)] = rmats_input_gene_level_df['gene_CIR_read_count'] * rmats_input_gene_level_df['IncFormLen'] / (rmats_input_gene_level_df['IncFormLen'] - rmats_input_gene_level_df['SkipFormLen']) 
                        rmats_input_gene_level_df['SC_S2_R%d' % (i+1)] = rmats_input_gene_level_df['gene_CIR_read_count'] + rmats_input_gene_level_df['gene_CER_read_count'] - rmats_input_gene_level_df['IC_S2_R%d' % (i+1)]
                        rmats_input_gene_level_df.drop(labels=['gene_CIR_read_count', 'gene_CER_read_count'], axis=1, inplace=True)   
                        
                rmats_input_gene_level_df['IC_S1'] = rmats_input_gene_level_df.filter(regex=r'IC_S1').apply(lambda row: ','.join([str(item) for item in row.values]), axis=1)
                rmats_input_gene_level_df['SC_S1'] = rmats_input_gene_level_df.filter(regex=r'SC_S1').apply(lambda row: ','.join([str(item) for item in row.values]), axis=1)
                rmats_input_gene_level_df['IC_S2'] = rmats_input_gene_level_df.filter(regex=r'IC_S2').apply(lambda row: ','.join([str(item) for item in row.values]), axis=1)
                rmats_input_gene_level_df['SC_S2'] = rmats_input_gene_level_df.filter(regex=r'SC_S2').apply(lambda row: ','.join([str(item) for item in row.values]), axis=1)
                rmats_input_gene_level_df = rmats_input_gene_level_df.loc[:,['gene_id', 'IC_S1', 'SC_S1', 'IC_S2', 'SC_S2', 'IncFormLen', 'SkipFormLen']]  
                
                rmats_input_gene_level_df = self.filter_invalid_rows(rmats_input_gene_level_df)
                
                rmats_input_gene_level_file = self.params['name'] + ".diff.rMATSinput.IRI.genes.txt" 
                self.rmats_input_gene_level_file_fullpath = os.path.join(self.temp_dir, rmats_input_gene_level_file)
                logging.info("Writing gene level rMATS inputs to file: {}".format(self.rmats_input_gene_level_file_fullpath))
                rmats_input_gene_level_df.to_csv(self.rmats_input_gene_level_file_fullpath, index=None, sep='\t', na_rep="NA") 
                
        def run_rmats_intron_level(self):
                rmats_script_dir = pkg_resources.resource_filename('IRTools', "utility/rMATS")
                rmats_script_fullpath = os.path.join(rmats_script_dir, 'rMATS.sh')
                rmats_intron_level_output_temp_dir = os.path.join(self.temp_dir, 'rMATS_intron_level_output')
                
                logging.info('Run rMATS for differential IR in intron level')
                rmats_cmd = rmats_script_fullpath + " -d " + self.rmats_input_intron_level_file_fullpath + " -o " + rmats_intron_level_output_temp_dir + " -c " + str(self.params['cutoff']) + " -p 4 -t " + self.params['analysistype']
                p = subprocess.Popen(rmats_cmd, shell=True)
                p.wait()
                
                rmats_result_intron_level_df = pd.read_csv(os.path.join(rmats_intron_level_output_temp_dir, 'rMATS_Result.txt'), header=0, sep='\t').loc[:, ['CIR_id', 'PValue', 'FDR', 'IncLevel1', 'IncLevel2', 'IncLevelDifference']]
                rmats_result_intron_level_df['IncLevelDifference'] = - rmats_result_intron_level_df['IncLevelDifference']
                rmats_result_intron_level_df.rename(columns={'IncLevel1': 'intron_IRI_S1', 'IncLevel2': 'intron_IRI_S2', 'IncLevelDifference': 'intron_IRI_difference'}, inplace=True)
                
                outfile = self.params['name'] + '.diff.IRI.introns.txt'
                outfile_fullpath = os.path.join(self.params['outdir'], outfile)
                logging.info("Writing intron level differential IR result to file: %s" % outfile_fullpath)
                rmats_result_intron_level_df.to_csv(outfile_fullpath, index=None, sep='\t')    
                
        def run_rmats_gene_level(self):
                rmats_script_dir = pkg_resources.resource_filename('IRTools', "utility/rMATS")
                rmats_script_fullpath = os.path.join(rmats_script_dir, 'rMATS.sh')
                rmats_gene_level_output_temp_dir = os.path.join(self.temp_dir, 'rMATS_gene_level_output')
                
                logging.info('Run rMATS for differential IR in gene level')
                rmats_cmd = rmats_script_fullpath + " -d " + self.rmats_input_gene_level_file_fullpath + " -o " + rmats_gene_level_output_temp_dir + " -c " + str(self.params['cutoff']) + " -p 4 -t " + self.params['analysistype']
                p = subprocess.Popen(rmats_cmd, shell=True)
                p.wait()
                
                rmats_result_gene_level_df = pd.read_csv(os.path.join(rmats_gene_level_output_temp_dir, 'rMATS_Result.txt'), header=0, sep='\t').loc[:, ['gene_id', 'PValue', 'FDR', 'IncLevel1', 'IncLevel2', 'IncLevelDifference']]
                rmats_result_gene_level_df['IncLevelDifference'] = - rmats_result_gene_level_df['IncLevelDifference']
                rmats_result_gene_level_df.rename(columns={'IncLevel1': 'gene_IRI_S1', 'IncLevel2': 'gene_IRI_S2', 'IncLevelDifference': 'gene_IRI_difference'}, inplace=True)
                
                outfile = self.params['name'] + '.diff.IRI.genes.txt'
                outfile_fullpath = os.path.join(self.params['outdir'], outfile)
                logging.info("Writing gene level differential IR result to file: %s" % outfile_fullpath)
                rmats_result_gene_level_df.to_csv(outfile_fullpath, index=None, sep='\t')                 


class IRC_diff(object):      
        def __init__(self, args):
                self.params = args.__dict__.copy()
                
                self.temp_dir = self.check_temp_dir(self.params['outdir']) 
                print("\tNote: Running \"IRTools diff\" will produce some intermediate files saved in directory: {}/".format(self.temp_dir))
                sys.stdout.flush()   
                
                self.logger = logging.getLogger()  
                
        @staticmethod                        
        def check_temp_dir(outdir):
                temp_dir = os.path.join(outdir, "temp")
                if not os.path.exists( temp_dir ):
                        try:
                                os.makedirs( temp_dir ) 
                        except:
                                temp_dir = outdir
                                             
                return temp_dir  
        
        def run_IRC_quant_for_all_samples(self, args):
                logging.info("Perform \"IRTools quant\" for all replciates from both samples")
                self.logger.disabled = True
                
                filtered_CIR_id_list = []
                
                s1files_list = self.params['s1files'].split(',')
                s2files_list = self.params['s2files'].split(',')                

                IRC_junction_level_df_s1_list = []
                IRC_junction_level_df_s2_list = []
                
                IRC_intron_level_df_s1_list = []
                IRC_intron_level_df_s2_list = []                
                
                CIR_counts_s1_list = []
                CIR_counts_s2_list = []
                
                IRC_quanter = IRC_quant(args)
                IRC_quanter.params['outdir'] = self.temp_dir 
                
                for i, s1file in enumerate(s1files_list):
                        IRC_quanter.params['name'] = self.params['name'] + "_S1_R%d" % (i+1)
                        IRC_quanter.params['altfile'] = s1file
                        
                        IRC_quanter.quant()
                        IRC_quanter.output_IRC_junction_level()
                        IRC_junction_level_df_s1_list.append(IRC_quanter.IRC_junction_level_df)
                        
                        IRC_quanter.output_IRC_intron_level()
                        IRC_intron_level_df_s1_list.append(IRC_quanter.IRC_intron_level_df)
                        
                        CIR_counts_s1_list.append(copy.deepcopy(IRC_quanter.CIR_counts))
                        filtered_CIR_id_list.extend(IRC_quanter.filtered_CIR_id_list)
                                               
                for i, s2file in enumerate(s2files_list):
                        IRC_quanter.params['name'] = self.params['name'] + "_S2_R%d" % (i+1)
                        IRC_quanter.params['altfile'] = s2file
                        
                        IRC_quanter.quant()
                        IRC_quanter.output_IRC_junction_level()
                        IRC_junction_level_df_s2_list.append(IRC_quanter.IRC_junction_level_df)
                        
                        IRC_quanter.output_IRC_intron_level()
                        IRC_intron_level_df_s2_list.append(IRC_quanter.IRC_intron_level_df)
                        
                        CIR_counts_s2_list.append(copy.deepcopy(IRC_quanter.CIR_counts))
                        filtered_CIR_id_list.extend(IRC_quanter.filtered_CIR_id_list)
                        
                filtered_CIR_id_list = list(set(filtered_CIR_id_list))
                
                for i, IRC_intron_level_df in enumerate(IRC_intron_level_df_s1_list):
                        IRC_intron_level_df_s1_list[i] = IRC_intron_level_df[IRC_intron_level_df.CIR_id.isin(filtered_CIR_id_list) == False]
                
                for i, IRC_intron_level_df in enumerate(IRC_intron_level_df_s2_list):
                        IRC_intron_level_df_s2_list[i] = IRC_intron_level_df[IRC_intron_level_df.CIR_id.isin(filtered_CIR_id_list) == False]                     
                
                self.IRC_junction_level_data = {'s1_data': IRC_junction_level_df_s1_list,
                                                's2_data': IRC_junction_level_df_s2_list}  
                
                self.IRC_intron_level_data = {'s1_data': IRC_intron_level_df_s1_list,
                                              's2_data': IRC_intron_level_df_s2_list} 
                
                IRC_gene_level_df_s1_list = []
                IRC_gene_level_df_s2_list = []                
                
                for i, s1file in enumerate(s1files_list):
                        IRC_quanter.params['name'] = self.params['name'] + "_S1_R%d" % (i+1)
                        
                        IRC_quanter.CIR_counts = CIR_counts_s1_list[i]
                        IRC_quanter.output_IRC_gene_level(filtered_CIR_id_list)
                        IRC_gene_level_df_s1_list.append(IRC_quanter.IRC_gene_level_df)
                
                        self.logger.disabled = False
                        logging.info("Sample: " + IRC_quanter.params['name'])                   
                        IRC_quanter.output_IRC_genome_wide()
                        self.logger.disabled = True
                        
                for i, s2file in enumerate(s2files_list):
                        IRC_quanter.params['name'] = self.params['name'] + "_S2_R%d" % (i+1)
                        
                        IRC_quanter.CIR_counts = CIR_counts_s2_list[i]
                        IRC_quanter.output_IRC_gene_level(filtered_CIR_id_list)
                        IRC_gene_level_df_s2_list.append(IRC_quanter.IRC_gene_level_df)
                
                        self.logger.disabled = False
                        logging.info("Sample: " + IRC_quanter.params['name'])                   
                        IRC_quanter.output_IRC_genome_wide()
                        self.logger.disabled = True
                        
                self.IRC_gene_level_data = {'s1_data': IRC_gene_level_df_s1_list,
                                            's2_data': IRC_gene_level_df_s2_list}
                
                self.logger.disabled = False  
                
        @staticmethod        
        def filter_invalid_rows(df):
                df['sum_IC_S1'] = df.apply(lambda row: sum([float(x) for x in row['IC_S1'].split(',')]), axis=1)
                df['sum_SC_S1'] = df.apply(lambda row: sum([float(x) for x in row['SC_S1'].split(',')]), axis=1)
                
                df['sum_IC_S2'] = df.apply(lambda row: sum([float(x) for x in row['IC_S2'].split(',')]), axis=1)
                df['sum_SC_S2'] = df.apply(lambda row: sum([float(x) for x in row['SC_S2'].split(',')]), axis=1)   
                
                df = df[(df['sum_IC_S1'] + df['sum_SC_S1'] > 0) & (df['sum_IC_S2'] + df['sum_SC_S2'] > 0) & ((df['sum_IC_S1']  != 0) | (df['sum_IC_S2'] != 0)) & ((df['sum_SC_S1']  != 0) | (df['sum_SC_S2'] != 0)) & (df['IncFormLen'] != 0) & (df['SkipFormLen'] != 0)]
                return df.drop(labels=['sum_IC_S1', 'sum_SC_S1', 'sum_IC_S2', 'sum_SC_S2'], axis=1)
        
        def generate_rmats_input_junction_level(self):
                logging.info("Generate inputs for rMATS for differential IR in junction level")
                
                rmats_input_junction_level_df = None
                
                for i, IRC_junction_level_df in enumerate(self.IRC_junction_level_data['s1_data']):
                        if rmats_input_junction_level_df is None:
                                rmats_input_junction_level_df = IRC_junction_level_df.loc[:,['CJ_id', 'CJ_retained_reads', 'CJ_spliced_reads']]    
                                rmats_input_junction_level_df['IncFormLen'] = 1
                                rmats_input_junction_level_df['SkipFormLen'] = 1                                
                        else:
                                rmats_input_junction_level_df = rmats_input_junction_level_df.merge(IRC_junction_level_df.loc[:,['CJ_id', 'CJ_retained_reads', 'CJ_spliced_reads']], on='CJ_id')
                                
                        rmats_input_junction_level_df['IC_S1_R%d' % (i+1)] = rmats_input_junction_level_df['CJ_retained_reads']
                        rmats_input_junction_level_df['SC_S1_R%d' % (i+1)] = rmats_input_junction_level_df['CJ_spliced_reads']
                        rmats_input_junction_level_df.drop(labels=['CJ_retained_reads', 'CJ_spliced_reads'], axis=1, inplace=True)                        
                                
                for i, IRC_junction_level_df in enumerate(self.IRC_junction_level_data['s2_data']):
                        rmats_input_junction_level_df = rmats_input_junction_level_df.merge(IRC_junction_level_df.loc[:,['CJ_id', 'CJ_retained_reads', 'CJ_spliced_reads']], on='CJ_id')
                        rmats_input_junction_level_df['IC_S2_R%d' % (i+1)] = rmats_input_junction_level_df['CJ_retained_reads']
                        rmats_input_junction_level_df['SC_S2_R%d' % (i+1)] = rmats_input_junction_level_df['CJ_spliced_reads']
                        rmats_input_junction_level_df.drop(labels=['CJ_retained_reads', 'CJ_spliced_reads'], axis=1, inplace=True)                              
                        
                rmats_input_junction_level_df['IC_S1'] = rmats_input_junction_level_df.filter(regex=r'IC_S1').apply(lambda row: ','.join([str(item) for item in row.values]), axis=1)
                rmats_input_junction_level_df['SC_S1'] = rmats_input_junction_level_df.filter(regex=r'SC_S1').apply(lambda row: ','.join([str(item) for item in row.values]), axis=1)
                rmats_input_junction_level_df['IC_S2'] = rmats_input_junction_level_df.filter(regex=r'IC_S2').apply(lambda row: ','.join([str(item) for item in row.values]), axis=1)
                rmats_input_junction_level_df['SC_S2'] = rmats_input_junction_level_df.filter(regex=r'SC_S2').apply(lambda row: ','.join([str(item) for item in row.values]), axis=1)
                rmats_input_junction_level_df = rmats_input_junction_level_df.loc[:,['CJ_id', 'IC_S1', 'SC_S1', 'IC_S2', 'SC_S2', 'IncFormLen', 'SkipFormLen']]  
                
                rmats_input_junction_level_df = self.filter_invalid_rows(rmats_input_junction_level_df)
                
                rmats_input_junction_level_file = self.params['name'] + ".diff.rMATSinput.IRC.junctions.txt" 
                self.rmats_input_junction_level_file_fullpath = os.path.join(self.temp_dir, rmats_input_junction_level_file)
                logging.info("Writing junction level rMATS inputs to file: {}".format(self.rmats_input_junction_level_file_fullpath))
                rmats_input_junction_level_df.to_csv(self.rmats_input_junction_level_file_fullpath, index=None, sep='\t', na_rep="NA")
                
        def generate_rmats_input_intron_level(self):
                logging.info("Generate inputs for rMATS for differential IR in intron level")
                
                rmats_input_intron_level_df = None
                
                for i, IRC_intron_level_df in enumerate(self.IRC_intron_level_data['s1_data']):
                        if rmats_input_intron_level_df is None:
                                rmats_input_intron_level_df = IRC_intron_level_df.loc[:,['CIR_id', "CIR_5'retained_reads", "CIR_3'retained_reads", 'CIR_spliced_reads']]    
                                rmats_input_intron_level_df['IncFormLen'] = 100
                                rmats_input_intron_level_df['SkipFormLen'] = 100                                
                        else:
                                rmats_input_intron_level_df = rmats_input_intron_level_df.merge(IRC_intron_level_df.loc[:,['CIR_id', "CIR_5'retained_reads", "CIR_3'retained_reads", 'CIR_spliced_reads']], on='CIR_id')
                                
                        rmats_input_intron_level_df['IC_S1_R%d' % (i+1)] = (rmats_input_intron_level_df["CIR_5'retained_reads"] + rmats_input_intron_level_df["CIR_3'retained_reads"]) / 2.0
                        rmats_input_intron_level_df['SC_S1_R%d' % (i+1)] = rmats_input_intron_level_df['CIR_spliced_reads']
                        rmats_input_intron_level_df.drop(labels=["CIR_5'retained_reads", "CIR_3'retained_reads", 'CIR_spliced_reads'], axis=1, inplace=True)                        
                                
                for i, IRC_intron_level_df in enumerate(self.IRC_intron_level_data['s2_data']):
                        rmats_input_intron_level_df = rmats_input_intron_level_df.merge(IRC_intron_level_df.loc[:,['CIR_id', "CIR_5'retained_reads", "CIR_3'retained_reads", 'CIR_spliced_reads']], on='CIR_id')
                        rmats_input_intron_level_df['IC_S2_R%d' % (i+1)] = (rmats_input_intron_level_df["CIR_5'retained_reads"] + rmats_input_intron_level_df["CIR_3'retained_reads"]) / 2.0
                        rmats_input_intron_level_df['SC_S2_R%d' % (i+1)] = rmats_input_intron_level_df['CIR_spliced_reads']
                        rmats_input_intron_level_df.drop(labels=["CIR_5'retained_reads", "CIR_3'retained_reads", 'CIR_spliced_reads'], axis=1, inplace=True) 
                        
                rmats_input_intron_level_df['IC_S1'] = rmats_input_intron_level_df.filter(regex=r'IC_S1').apply(lambda row: ','.join([str(item) for item in row.values]), axis=1)
                rmats_input_intron_level_df['SC_S1'] = rmats_input_intron_level_df.filter(regex=r'SC_S1').apply(lambda row: ','.join([str(item) for item in row.values]), axis=1)
                rmats_input_intron_level_df['IC_S2'] = rmats_input_intron_level_df.filter(regex=r'IC_S2').apply(lambda row: ','.join([str(item) for item in row.values]), axis=1)
                rmats_input_intron_level_df['SC_S2'] = rmats_input_intron_level_df.filter(regex=r'SC_S2').apply(lambda row: ','.join([str(item) for item in row.values]), axis=1)
                rmats_input_intron_level_df = rmats_input_intron_level_df.loc[:,['CIR_id', 'IC_S1', 'SC_S1', 'IC_S2', 'SC_S2', 'IncFormLen', 'SkipFormLen']] 
                
                rmats_input_intron_level_df = self.filter_invalid_rows(rmats_input_intron_level_df)
                
                rmats_input_intron_level_file = self.params['name'] + ".diff.rMATSinput.IRC.introns.txt" 
                self.rmats_input_intron_level_file_fullpath = os.path.join(self.temp_dir, rmats_input_intron_level_file)
                logging.info("Writing intron level rMATS inputs to file: {}".format(self.rmats_input_intron_level_file_fullpath))
                rmats_input_intron_level_df.to_csv(self.rmats_input_intron_level_file_fullpath, index=None, sep='\t', na_rep="NA") 
                
        def generate_rmats_input_gene_level(self):
                logging.info("Generate inputs for rMATS for differential IR in gene level")
                
                rmats_input_gene_level_df = None
                
                for i, IRC_gene_level_df in enumerate(self.IRC_gene_level_data['s1_data']):
                        if rmats_input_gene_level_df is None:
                                rmats_input_gene_level_df = IRC_gene_level_df.loc[:,['gene_id', 'gene_retained_reads', 'gene_spliced_reads']]    
                                rmats_input_gene_level_df['IncFormLen'] = 100
                                rmats_input_gene_level_df['SkipFormLen'] = 100                               
                        else:
                                rmats_input_gene_level_df = rmats_input_gene_level_df.merge(IRC_gene_level_df.loc[:,['gene_id', 'gene_retained_reads', 'gene_spliced_reads']], on='gene_id')
                                
                        rmats_input_gene_level_df['IC_S1_R%d' % (i+1)] = rmats_input_gene_level_df['gene_retained_reads']
                        rmats_input_gene_level_df['SC_S1_R%d' % (i+1)] = rmats_input_gene_level_df['gene_spliced_reads']
                        rmats_input_gene_level_df.drop(labels=['gene_retained_reads', 'gene_spliced_reads'], axis=1, inplace=True)                        
                                
                for i, IRC_gene_level_df in enumerate(self.IRC_gene_level_data['s2_data']):
                        rmats_input_gene_level_df = rmats_input_gene_level_df.merge(IRC_gene_level_df.loc[:,['gene_id', 'gene_retained_reads', 'gene_spliced_reads']], on='gene_id')
                        rmats_input_gene_level_df['IC_S2_R%d' % (i+1)] = rmats_input_gene_level_df['gene_retained_reads']
                        rmats_input_gene_level_df['SC_S2_R%d' % (i+1)] = rmats_input_gene_level_df['gene_spliced_reads']
                        rmats_input_gene_level_df.drop(labels=['gene_retained_reads', 'gene_spliced_reads'], axis=1, inplace=True)                           
                        
                rmats_input_gene_level_df['IC_S1'] = rmats_input_gene_level_df.filter(regex=r'IC_S1').apply(lambda row: ','.join([str(item) for item in row.values]), axis=1)
                rmats_input_gene_level_df['SC_S1'] = rmats_input_gene_level_df.filter(regex=r'SC_S1').apply(lambda row: ','.join([str(item) for item in row.values]), axis=1)
                rmats_input_gene_level_df['IC_S2'] = rmats_input_gene_level_df.filter(regex=r'IC_S2').apply(lambda row: ','.join([str(item) for item in row.values]), axis=1)
                rmats_input_gene_level_df['SC_S2'] = rmats_input_gene_level_df.filter(regex=r'SC_S2').apply(lambda row: ','.join([str(item) for item in row.values]), axis=1)
                rmats_input_gene_level_df = rmats_input_gene_level_df.loc[:,['gene_id', 'IC_S1', 'SC_S1', 'IC_S2', 'SC_S2', 'IncFormLen', 'SkipFormLen']]  
                
                rmats_input_gene_level_df = self.filter_invalid_rows(rmats_input_gene_level_df)
                
                rmats_input_gene_level_file = self.params['name'] + ".diff.rMATSinput.IRC.genes.txt" 
                self.rmats_input_gene_level_file_fullpath = os.path.join(self.temp_dir, rmats_input_gene_level_file)
                logging.info("Writing gene level rMATS inputs to file: {}".format(self.rmats_input_gene_level_file_fullpath))
                rmats_input_gene_level_df.to_csv(self.rmats_input_gene_level_file_fullpath, index=None, sep='\t', na_rep="NA") 
                
        def run_rmats_junction_level(self):
                rmats_script_dir = pkg_resources.resource_filename('IRTools', "utility/rMATS")
                rmats_script_fullpath = os.path.join(rmats_script_dir, 'rMATS.sh')
                rmats_junction_level_output_temp_dir = os.path.join(self.temp_dir, 'rMATS_junction_level_output')
                
                logging.info('Run rMATS for differential IR in junction level')
                rmats_cmd = rmats_script_fullpath + " -d " + self.rmats_input_junction_level_file_fullpath + " -o " + rmats_junction_level_output_temp_dir + " -c " + str(self.params['cutoff']) + " -p 4 -t " + self.params['analysistype']
                p = subprocess.Popen(rmats_cmd, shell=True)
                p.wait()
                
                rmats_result_junction_level_df = pd.read_csv(os.path.join(rmats_junction_level_output_temp_dir, 'rMATS_Result.txt'), header=0, sep='\t').loc[:, ['CJ_id', 'PValue', 'FDR', 'IncLevel1', 'IncLevel2', 'IncLevelDifference']]
                rmats_result_junction_level_df['IncLevelDifference'] = - rmats_result_junction_level_df['IncLevelDifference']
                rmats_result_junction_level_df.rename(columns={'IncLevel1': 'junction_IRC_S1', 'IncLevel2': 'junction_IRC_S2', 'IncLevelDifference': 'junction_IRC_difference'}, inplace=True)
                
                outfile = self.params['name'] + '.diff.IRC.junctions.txt'
                outfile_fullpath = os.path.join(self.params['outdir'], outfile)
                logging.info("Writing junction level differential IR result to file: %s" % outfile_fullpath)
                rmats_result_junction_level_df.to_csv(outfile_fullpath, index=None, sep='\t') 
                
        def run_rmats_intron_level(self):
                rmats_script_dir = pkg_resources.resource_filename('IRTools', "utility/rMATS")
                rmats_script_fullpath = os.path.join(rmats_script_dir, 'rMATS.sh')
                rmats_intron_level_output_temp_dir = os.path.join(self.temp_dir, 'rMATS_intron_level_output')
                
                logging.info('Run rMATS for differential IR in intron level')
                rmats_cmd = rmats_script_fullpath + " -d " + self.rmats_input_intron_level_file_fullpath + " -o " + rmats_intron_level_output_temp_dir + " -c " + str(self.params['cutoff']) + " -p 4 -t " + self.params['analysistype']
                p = subprocess.Popen(rmats_cmd, shell=True)
                p.wait()
                
                rmats_result_intron_level_df = pd.read_csv(os.path.join(rmats_intron_level_output_temp_dir, 'rMATS_Result.txt'), header=0, sep='\t').loc[:, ['CIR_id', 'PValue', 'FDR', 'IncLevel1', 'IncLevel2', 'IncLevelDifference']]
                rmats_result_intron_level_df['IncLevelDifference'] = - rmats_result_intron_level_df['IncLevelDifference']
                rmats_result_intron_level_df.rename(columns={'IncLevel1': 'intron_IRC_S1', 'IncLevel2': 'intron_IRC_S2', 'IncLevelDifference': 'intron_IRC_difference'}, inplace=True)
                
                outfile = self.params['name'] + '.diff.IRC.introns.txt'
                outfile_fullpath = os.path.join(self.params['outdir'], outfile)
                logging.info("Writing intron level differential IR result to file: %s" % outfile_fullpath)
                rmats_result_intron_level_df.to_csv(outfile_fullpath, index=None, sep='\t') 
                
        def run_rmats_gene_level(self):
                rmats_script_dir = pkg_resources.resource_filename('IRTools', "utility/rMATS")
                rmats_script_fullpath = os.path.join(rmats_script_dir, 'rMATS.sh')
                rmats_gene_level_output_temp_dir = os.path.join(self.temp_dir, 'rMATS_gene_level_output')
                
                logging.info('Run rMATS for differential IR in gene level')
                rmats_cmd = rmats_script_fullpath + " -d " + self.rmats_input_gene_level_file_fullpath + " -o " + rmats_gene_level_output_temp_dir + " -c " + str(self.params['cutoff']) + " -p 4 -t " + self.params['analysistype']
                p = subprocess.Popen(rmats_cmd, shell=True)
                p.wait()
                
                rmats_result_gene_level_df = pd.read_csv(os.path.join(rmats_gene_level_output_temp_dir, 'rMATS_Result.txt'), header=0, sep='\t').loc[:, ['gene_id', 'PValue', 'FDR', 'IncLevel1', 'IncLevel2', 'IncLevelDifference']]
                rmats_result_gene_level_df['IncLevelDifference'] = - rmats_result_gene_level_df['IncLevelDifference']
                rmats_result_gene_level_df.rename(columns={'IncLevel1': 'gene_IRC_S1', 'IncLevel2': 'gene_IRC_S2', 'IncLevelDifference': 'gene_IRC_difference'}, inplace=True)
                
                outfile = self.params['name'] + '.diff.IRC.genes.txt'
                outfile_fullpath = os.path.join(self.params['outdir'], outfile)
                logging.info("Writing gene level differential IR result to file: %s" % outfile_fullpath)
                rmats_result_gene_level_df.to_csv(outfile_fullpath, index=None, sep='\t')  

def run(args):
        if args.quanttype == "IRI":
                IRI_differ = IRI_diff(args)
                IRI_differ.run_IRI_quant_for_all_samples(args)
                IRI_differ.generate_rmats_input_intron_level()
                IRI_differ.generate_rmats_input_gene_level()
                IRI_differ.run_rmats_intron_level()
                IRI_differ.run_rmats_gene_level()
                
        elif args.quanttype == "IRC":
                IRC_differ = IRC_diff(args)
                IRC_differ.run_IRC_quant_for_all_samples(args)
                IRC_differ.generate_rmats_input_junction_level()
                IRC_differ.generate_rmats_input_intron_level()
                IRC_differ.generate_rmats_input_gene_level()
                IRC_differ.run_rmats_junction_level()
                IRC_differ.run_rmats_intron_level()
                IRC_differ.run_rmats_gene_level()











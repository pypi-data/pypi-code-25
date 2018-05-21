import click, json, pandas as pd, os, numpy as np



#######################
#### RUN CLI GROUP ####

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], max_content_width=90)

@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='0.1')
def pairfastq():
    pass


##########################
#### PAIR FASTQ FILES ####

@pairfastq.command()
@click.option('-fq','--fastq',help='Fastq file(s) for pairing. Comma delimited.', type=click.Path(exists=False))
@click.option('-csv','--config',default = './config.csv', show_default=True, help='Csv configuration file specifying reads 1 data, reads 2 data, and conditions data in columns r1, r2, and condition, respectively.',type=click.Path(exists=False))
@click.option('-o','--output_file',default = 'cwl.output.json', show_default=True, help='Cwl output json file array, essentially a json containing fastq file pairs.') # remember to inherit metadata from the input files
@click.option('-w','--work_dir',default = './', show_default=True, help='Work directory.',type=click.Path(exists=False))
def pair_fastq(fastq,config,output_file,work_dir):
    fastq = np.array(map(os.path.abspath,fastq.split(',')))
    df = pd.read_csv(config)
    fastq_pairs = []
    unprocessed_pairs = [['Sample1','Sample2']]
    fastq_pairs_all = df[['r1','r2']].values.tolist()
    #print(fastq)
    fastq_check = []
    new_fastq_dict = {}
    for r1,r2 in fastq_pairs_all:
        r1_test,r2_test = tuple(map(lambda y: fastq[np.vectorize(lambda x: y in x)(fastq)][0],[r1,r2]))#tuple(map(os.path.abspath,[r1,r2]))
        if r1_test.tolist() and r2_test.tolist():
            fastq_pairs.append(map(lambda path: {'class':'File','path':path},[r1_test[0],r2_test[0]]))
            new_fastq_dict[r1] = r1_test[0]
            new_fastq_dict[r2] = r2_test[0]
            fastq_check.append(r1)
        else:
            unprocessed_pairs.append([r1,r2])

    unprocessed_pairs.extend([(fq,'') for fq in set(fastq)-set(reduce(lambda x, y: x+y, fastq_pairs_all))])

    unprocessed_pairs = '\n'.join('\t'.join(unprocessed_pair) for unprocessed_pair in unprocessed_pairs)

    with open(work_dir+'/unprocessed_pairs.txt','w') as f:
        f.write(unprocessed_pairs)

    fastq_pairs_dict = {"fastq_pairs":fastq_pairs,"unprocessed_pairs":{"class":'File',"path":os.path.abspath(work_dir)+'/unprocessed_pairs.txt'}}

    df = df[df['r1'].isin(fastq_check).values]
    if 'condition' in list(df):
        df = df.iloc[np.argsort(df['condition']),:].reset_index(drop=True)
    #print(df[['r1','r2']].values.shape)
    if df[['r1','r2']].values.tolist():
        #print(df[['r1','r2']].values.tolist())
        df['r1','r2'] = [map(lambda x: new_fastq_dict[x], l) for l in df[['r1','r2']].values.tolist()] #np.apply_along_axis(lambda x: np.vectorize(os.path.abspath)(x),array=df[['r1','r2']].values,axis=1)
    df.to_csv(work_dir+'/output.paired_fastq.csv')

    with open(output_file,'w') as f:
        json.dump(fastq_pairs_dict,f)


#### RUN CLI ####

if __name__ == '__main__':
    pairfastq()
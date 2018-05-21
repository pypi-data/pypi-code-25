import click, json, pandas as pd, os, numpy as np, re
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import pairwise_distances
from MulticoreTSNE import MulticoreTSNE as TSNE
from sklearn.manifold import MDS
import plotly.offline as py
import plotly.graph_objs as go


class RNASeqPlot:
    def __init__(self, count_matrix, normalized):
        self.count_matrix = count_matrix # this should be a dataframe, import from csv
        self.normalized = normalized
        self.samples = list(self.count_matrix) # grab sample names

    def normalize(self, transcript_file = '', feature_name = 'gene', work_dir='./'):
        if hasattr(self,'TPM') == 0:
            df = pd.read_table(transcript_file,sep='\t',names=['seqname', 'source', 'feature', 'start', 'end', 'score', 'strand', 'frame' 'attributes'],header=None)
            df = df[df['feature'] == feature_name]
            df['gene_id'] = df['attributes'].map(lambda x: x.split()[1].translate(None,'";'))
            df = df[df['gene_id'].isin(np.array(self.count_matrix.index)).as_matrix()]
            df = df.loc[np.array(list(self.count_matrix.index)),:]
            df['length_kb'] = (df['end'].as_matrix() - (df['start'].as_matrix() - 1))/1000.
            self.RPK = self.count_matrix.div(df['length_kb'], axis=0)
            self.TPM = self.RPK.div(self.RPK.as_matrix().sum(axis=0),axis=1)
        self.original_count_matrix = self.count_matrix.copy()
        self.count_matrix = self.TPM
        self.normalized = True
        self.TPM.to_csv(work_dir+'normalized_count_matrix_TPM.csv')

    def denormalize(self):
        self.count_matrix = self.original_count_matrix.copy()
        self.normalized = False

    def compute_distance(self, metric='correlation'):
        self.distance = pd.DataFrame(pairwise_distances(self.count_matrix.T,metric=metric),index=self.samples,columns=self.samples)

    def plot(self, work_dir='./'):
        plt.figure()
        sns.heatmap(self.count_matrix)
        plt.savefig(work_dir+'/count_matrix.png',dpi=300,figsize=(1000,1000))
        plt.figure()
        sns.heatmap(self.distance)
        plt.savefig(work_dir+'/distance_matrix.png',dpi=300,figsize=(1000,1000))

    def transform(self,transform='mds',n_jobs=4): # MDS or TSNE transform
        self.transform_algorithm = transform
        transform_dict = {'tsne': TSNE(n_components=3, n_jobs=n_jobs, metric='precomputed'),
                          'mds': MDS(n_components=3, n_jobs=n_jobs, dissimilarity='precomputed')}
        self.t_data = transform_dict[transform].fit_transform(self.distance)


    def plotly_plot(self, output_file_prefix, work_dir='./'):
        py.plot(go.Figure(data=[
            go.Scatter3d(x=self.t_data[:, 0], y=self.t_data[:, 1], z=self.t_data[:, 2], mode='markers', marker=dict(size=3),
                         text=self.samples)]), filename=work_dir+'%s.%s.html' % (output_file_prefix, self.transform_algorithm),
                auto_open=False)


#######################
#### RUN CLI GROUP ####

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], max_content_width=90)

@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='0.1')
def rnaseq():
    pass



@rnaseq.command()
@click.option('-gtf','--gtf_file', default = '', show_default=True, help='Merged annotations file from Stringtie. Optional, must have if normalizing count matrix.', type=click.Path(exists=False))
@click.option('-csv','--count_matrix',default = './config.csv', show_default=True, help='Raw count matrix in CSV format, gene_id for rows and sample names on the columns. Typically output from prepDE.py from Stringtie.',type=click.Path(exists=False))
@click.option('-f','--feature',default = 'gene', show_default=True, help='Feature to use in gtf file.',type=click.Choice(['gene','transcript']))
@click.option('-n','--normalized', is_flag=True, help='Is the count matrix already normalized?')
@click.option('-w','--work_dir',default = './', show_default=True, help='Work directory.') # remember to inherit metadata from the input files
def plot_rnaseq(gtf_file,count_matrix, feature, normalized,work_dir):
    """Normalize an RNASeq Count Matrix, find correlation pairwise distance and plot its results via heatmap and MDS/TSNE transform."""
    # make dataframe count_matrix and import into RNASeqPlot
    work_dir +='/'
    count_mat_prefix = count_matrix[count_matrix.rfind('/')+1:count_matrix.rfind('.')]
    count_matrix = RNASeqPlot(pd.read_csv(count_matrix),normalized)
    if not count_matrix.normalized:
        count_matrix.normalize(gtf_file,feature,work_dir)
    count_matrix.compute_distance('correlation')
    count_matrix.plot(work_dir)
    count_matrix.transform('mds')
    count_matrix.plotly_plot(count_mat_prefix, work_dir)
    # still adding MDS TSNE transform, 3d plot via plotly

#### RUN CLI ####

if __name__ == '__main__':
    rnaseq()
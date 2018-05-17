import subprocess, os, numpy as np, click

######################
#### CIRCOS CLASS ####

class Circos:
    def __init__(self, karyotype, datasets): # datasets is either list or dict
        self.karyotype = karyotype
        self.datasets = datasets
        if type(self.datasets) == type([]):
            self.datasets = {fname:'red' for fname in self.datasets}

    def write_ideogram_config(self, filename='txideogram.conf'):
        with open(filename,'w') as f:
            f.write("""<ideogram>
                show = yes
                <spacing>
                default = 0.005r
                </spacing>
                radius    = 0.9r
                thickness = 40p
                fill      = yes
                show_label = yes
                label_font = default
                label_radius = 1.08r
                label_size = 40
                label_parallel = yes
                show_bands = yes
                fill_bands = yes
                </ideogram>""")
        self.ideogram = filename
        return filename

    def write_ticks_config(self, filename='txticks.conf'):
        with open(filename,'w') as f:
            f.write("""show_ticks = yes
                show_tick_labels = yes
                <ticks>
                radius = 1.01r
                color = black
                thickness = 2p
                multiplier = 1e-6
                format = %d
                <tick>
                spacing = 1u
                size = 5p
                </tick>
                <tick>
                spacing = 5u
                size = 10p
                show_label = yes
                label_size = 20p
                label_offset = 10p
                format = %d
                </tick>
                </ticks>""")
        self.ticks = filename
        return filename

    def write_data_config(self, filename='data.conf'):
        radii_dict = self.generate_radii()
        with open(filename,'w') as f:
            f.write('<plots>\n'+'\n'.join( # color = spectral-9-div\ncolor_alt = black,spectral-8-div,grey\nstroke_thickness = 1\nstroke_color = black\n
                """
            <plot>
            type = histogram
            file = %s
            fill_color = %s
            r0 = %fr
            r1 = %fr
            extend_bin = no
            orientation = out
            thickness = 1
            fill_under = yes
            max_gap = 5u
            </plot>
            """%((data_file,color)+(radii_dict[data_file]))
            for data_file,color in self.datasets.items())
            +'\n<rules>\n</rules>\n</plots>')
            self.data = filename
            return filename

    def generate_radii(self):
        f_names = self.datasets.keys()
        radii = np.linspace(0.40,0.80,len(f_names)+1)
        return dict(zip( f_names,[(radii[i],radii[i+1]) for i in range(len(radii)-1)]))

    def generate_config(self, ticks = 'txticks.conf', ideogram = 'txideogram.conf', data = 'data.conf', config='circos.conf'):
        self.data = data
        self.config = config
        self.ideogram,self.ticks = ideogram, ticks
        if hasattr(self, 'ticks'):
            self.write_ticks_config(self.ticks)
        if hasattr(self, 'ideogram'):
            self.write_ideogram_config(self.ideogram)
        if hasattr(self, 'data'):
            self.write_data_config(self.data)
        with open(self.config,'w') as f:
            f.write("""# circos.conf
                karyotype = %s
                chromosomes_units = 1000000
                chromosomes_display_default = yes
                <<include %s>>
                <<include %s>>
                <<include %s>>
                <image>
                <<include etc/image.conf>>
                </image>
                <<include etc/colors_fonts_patterns.conf>>
                <<include etc/housekeeping.conf>>
                """%(self.karyotype,self.ideogram,self.ticks,self.data))

    def run_circos(self, out_prefix = 'output', output_dir='./', pdf=False):
        subprocess.call('circos -conf %s -outputfile %s -outputdir %s'%(self.config,out_prefix,output_dir),shell=True)
        if pdf:
            subprocess.call('convert %s/%s.png %s/%s.pdf'%(os.path.abspath(output_dir),out_prefix,os.path.abspath(output_dir),out_prefix),shell=True)



#######################
#### RUN CLI GROUP ####

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], max_content_width=90)

@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='0.1')
def circosplot():
    pass

####################
#### RUN CIRCOS ####

@circosplot.command()
@click.option('-d','--data',help='Data file(s) for circos input.',multiple=True, type=click.Path(exists=False))
@click.option('-k','--karyotype',default = './karyotype.txt', show_default=True, help='Karyotype file.',type=click.Path(exists=False))
@click.option('-o','--out_prefix',default = 'output', show_default=True, help='Output prefix.')
@click.option('-w','--work_dir',default = './', show_default=True, help='Work directory.',type=click.Path(exists=False))
def circos(data,karyotype,out_prefix,work_dir):
    circos_obj = Circos(karyotype,data)
    circos_obj.generate_config()
    circos_obj.run_circos(out_prefix,work_dir)

#### RUN CLI ####

if __name__ == '__main__':
    circosplot()
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import range
from past.builtins import basestring
from builtins import object
from past.utils import old_div
from .common_fig import *
import os,shutil
import matplotlib.image as mpimg
from PyPDF2 import PdfFileMerger, PdfFileReader
import pybtex.plugin
import pybtex.database.input.bibtex
import matplotlib.patches as patches
from matplotlib.path import Path
from collections import OrderedDict
import pickle as pickle
import sys
import urllib.request, urllib.parse, urllib.error
#from matplotlib.pylab import *
init_plotting(presentation=True)

class Presentation(object):

 def __init__(self,**argv):

  self.slides = []
  self.sections = OrderedDict({'core':[]})
  self.current_section = 'core'

  if 'biblio_file' in list(argv.keys()) :
   parser = pybtex.database.input.bibtex.Parser()

   filename = argv['biblio_file']
   delete = False
   if '/' in filename:
    urllib.request.urlretrieve(filename,'tmp.' + filename.split('.')[-1])
    filename = 'tmp.' + filename.split('.')[-1]
    delete = True

   self.bib_data = parser.parse_file(filename)

   if delete:
    os.remove(filename)

 def add_section(self,section):
 
  self.sections.update({section:[]})
  self.current_section = section

 def add_slide(self,**argv):

  argv.setdefault('run',True)  
  argv.setdefault('model','custom')  
  argv.setdefault('texts',{})  
  argv.setdefault('figures',{})  
  argv.setdefault('title','')  
  argv.setdefault('bottom_text','')  

  if argv['model'] == 'title':
   self.make_title(argv)

  if argv['model'] == 'two_figures':
   self.make_two_figures(argv)

  if argv['model'] == 'one_figure':
   self.make_one_figure(argv)

  #Add commons------------------
  self.add_bottom_text(argv)
  self.sections[self.current_section].append(argv)

 def add_citation(self,names):

  if isinstance(names, basestring):
   names = [names]

  for n,name in enumerate(names):
   self.add_text(0.01,0.03 + n*0.035,self.cite(name),size=20,alignment='left')

 def add_text(self,x,y,text,color='black',alignment='center',size=30):

  self.sections[self.current_section][-1]['texts'].update({text:{'pos':[x,y],'color':color,\
                'alignment':alignment,'size':size}})

 def add_bullets(self,**argv):

  x = argv.setdefault('x',0.05)
  y = argv.setdefault('y',0.285)
  text = argv['text']

  deltay = 0.075
  for n,s in enumerate(text):
   tt = r'''$\bullet $  ''' + s
   self.sections[self.current_section][-1]['texts'].update({tt:{'pos':[x,y-(n-1)*deltay],'color':'black','alignment':'left','size':32}})



 def get_next_m(self):

  files = os.listdir('tmp')
  exist = True
  m = 0
  while exist:
   if not os.path.isfile('tmp/slide_' + str(m) + '.pdf'): 
    return m
   m +=1  


 def render(self):

  #Create directory---------------
  directory = 'tmp'
  if not os.path.exists(directory):
   os.makedirs(directory)
   #shutil.rmtree(directory)
 
  #load database--------------
  if os.path.isfile('tmp/slides.p'): 
   with open('tmp/slides.p') as f:
    slides_db = pickle.load(f)
  else:
   slides_db = {}
 
  slides_db_new = {}
  #--------------------------
  #-------

  list_files = []
  n = 0
  pagenumber = 0
  for section in self.sections:
   for slide in self.sections[section]:

     exist = False
     for m,slide_db in slides_db.items():
      if slide_db == slide:
       slides_db_new.update({m:slide})
       n += 1
       print('Include ' + str(n))
       list_files.append('tmp/slide_' + str(m) + '.pdf')
       exist = True
       break

     if not exist:
      self.render_slide(slide)
      m = self.get_next_m()
      n +=1
      print('Compile slide ' + str(n))
      slides_db_new.update({m:slide})
      
      savefig('tmp/slide_' + str(m) + '.pdf',dpi=500)  
      #savefig('tmp/slide_' + str(m) + '.pdf',dpi=100)  
      list_files.append('tmp/slide_' + str(m) + '.pdf')

  with open('tmp/slides.p', 'wb+') as f:
      pickle.dump(slides_db_new, f)
  #--------------------------

  self.slides = slides_db_new 
  #Create final presentation---------    
  merger = PdfFileMerger()
  for filename in list_files:
   merger.append(PdfFileReader(file(filename, 'rb')))
  namefile =  'slides.pdf'

  merger.write(namefile)

  #Reorder database
  self.reorder_database()

  #if show_pdf:
  # if sys.platform == 'darwin':
  #  os.system('play ' + namefile)
  # else:
  #  os.system('display ' + namefile)
 
 def get_slides(self):

  return self.sections


 def reorder_database(self):
  
  #update slides-------------------------
  with open('tmp/slides.p','rb') as f:
   slides_db = pickle.load(f)

  slides_db_new = {}

  index = sorted(list(range(len(list(slides_db.keys())))), key=lambda k: list(slides_db.keys())[k])
  for i,m in enumerate(index):
   old_index = list(slides_db.keys())[m]

   slides_db_new.update({i:slides_db[old_index]})
   os.system('mv tmp/slide_' + str(old_index) + '.pdf' + ' tmp/slide_tmp_' + str(i) + '.pdf' )

  #reordering
  files = os.listdir('tmp')
  for f in files:
   if len(f.split('_')) > 2:
    n = f.split('_')[2].split('.')[0]
    os.system('mv tmp/slide_tmp_' + str(n) + '.pdf' + ' tmp/slide_' + str(n)  + '.pdf')
  
  #write new database  
  with open('tmp/slides.p', 'wb+') as f:
    pickle.dump(slides_db_new, f)

 def render_slide(self,slide):

  close()
  init_plotting(presentation=True)

  #Text 

  self.plot_text(slide['texts'])

  #Figure
  for tt in list(slide['figures'].keys()):
   [x,y] = slide['figures'][tt]['pos']
   L = slide['figures'][tt]['size']
   self.plot_figure(tt,x,y,L)

  #if not slide['title'] == '':
  # plot([0,1],[0.91,0.91],color=c2,lw=2)

  xlim([0,1])
  ylim([0,1])

  #fig.canvas.mpl_connect('draw_event', on_draw)
   
  #-------------------------------

 def plot_text(self,slide):

   for tt in list(slide.keys()):
    tmp = slide[tt]
    pos = tmp['pos']
     #adjust font settings
    if tmp['size'] == 45:
     linespacing = 2.0
     N = 60
    else:
     linespacing = 1.5
     N = 200

    new_tt = tt.split(' ')
    tot = 1
    final_tt = ' '
    for t in new_tt:
     tot += 1 + len(t)
     if tot < N:
       final_tt += t + ' '
     else:   
       final_tt += '\n' + t + ' '
       tot = 1


    if not final_tt.isspace():
     text(pos[0],pos[1],final_tt,color=tmp['color'],\
        horizontalalignment=tmp['alignment'],\
        multialignment=tmp['alignment'],\
        fontsize=tmp['size'],linespacing=linespacing)


 def add_figure(self,x,y,L,filename):

  self.sections[self.current_section][-1]['figures'].update({filename:{'pos':[x,y],'size':L}})

 def make_title(self,argv):

  argv['texts'].update({argv['title']:{'pos':[0.5,0.75],'size':45,'alignment':'center','color':c1}})
  argv['texts'].update({argv['author']:{'pos':[0.5,0.5],'size':30,'alignment':'center','color':'black'}})
  argv['texts'].update({r'''\textit{''' + argv['affiliation'] + '}':{'pos':[0.5,0.45],'size':20,'alignment':'center','color':'black'}})
  argv['texts'].update({argv.setdefault('meeting',''):{'pos':[0.5,0.05],'size':20,'alignment':'center','color':'black'}})



 def plot_figure(self,filename,x,y,L):

   delete = False
   if '/' in filename:
    urllib.request.urlretrieve(filename,'tmp.' + filename.split('.')[-1])
    filename = 'tmp.' + filename.split('.')[-1]
    delete = True
    


   img=mpimg.imread(filename)
   r_img = old_div(float(np.shape(img)[0]),float(np.shape(img)[1]))

   r = 4.0/3.0*r_img
   coords =  [x-old_div(L,2),x+old_div(L,2),y-L/2*r,y+L/2*r]
   imshow(img,extent=coords,aspect='auto')
   plot([x-old_div(L,2),x-old_div(L,2),x+old_div(L,2),x+old_div(L,2),x-old_div(L,2)],\
        [y-r*L/2,y+r*L/2,y+r*L/2,y-r*L/2,y-r*L/2],color='w',lw=3)

   if delete:
    os.remove(filename)


 def add_bottom_text(self,argv):

    if not argv['bottom_text'] == '':   
     argv['texts'].update({argv['bottom_text'] :{'pos':[0.5,0.075],'size':40,'alignment':'center','color':'black'}})#,'multialignment':'center'}})


 def make_one_figure(self,argv):

   L = argv.setdefault('L',0.8)
   y = argv.setdefault('y',0.5)
   argv['figures'].update({argv['figure']:{'pos':[0.5,y],'size':L}})
  


 def make_two_figures(self,argv):

   #set defaults
   L1 = argv.setdefault('L1',0.4)
   dy1 = argv.setdefault('dy1',0.0)
   L2 = argv.setdefault('L2',0.4)
   x1 = argv.setdefault('x1',0.3)
   x2 = argv.setdefault('x2',0.7)
   y = argv.setdefault('y',0.5)
   #=====

   argv['figures'].update({argv['figure_1']:{'pos':[x1,y],'size':L1}})
   argv['figures'].update({argv['figure_2']:{'pos':[x2,y],'size':L2}})
    

   if 'upper_1' in list(argv.keys()): 
    argv['texts'].update({r'''\underline{'''+argv['upper_1'] + '}':{'pos':[x1,y+0.23],'size':40,'alignment':'center','color':'black'}})

   if 'upper_2' in list(argv.keys()): 
    argv['texts'].update({r'''\underline{''' + argv['upper_2'] + '}':{'pos':[x2,y+0.23],'size':40,'alignment':'center','color':'black'}})

   if 'lower_1' in list(argv.keys()): 
    argv['texts'].update({argv['lower_1'] :{'pos':[x1,dy1 + y-0.23],'size':16,'alignment':'center','color':'black'}})

   if 'lower_2' in list(argv.keys()): 
    argv['texts'].update({argv['lower_2'] :{'pos':[x2,y-0.23],'size':16,'alignment':'center','color':'black'}})





   #---------------------------------------
 def cite(self,ref):

   data = self.bib_data.entries[ref]

   #Authors-------------------------------------------
   n = len(data.persons['author'])
   strc = ''
   for i,au in enumerate(data.persons['author']):
    tmp = str(au).split(',')
    if tmp[1].count(' ') == 2:
     middle_name = ' ' + tmp[1][-1] + '. '
    else:
     middle_name = ' '

    name = tmp[1].strip()[0]
    last_name = tmp[0]
    author = name + '.' + middle_name + last_name


    if i == 0 and n > 2:
     strc += author 
     strc +=r''' \textit{et al.}, '''
     break

    if i == 0 and n == 2:
     strc += author 
     strc += ' and '

    if i == 1 and n == 2:
     strc += author 
     strc += ', '

   #---------------------------------------------
   strc += r'''\textit{'''+data.fields['journal']+ '}, '
   if len(data.fields['volume'])> 0:
    strc += data.fields['volume'] + ', '
   if len(data.fields['pages'])> 0:
    strc += data.fields['pages'] 
   strc += ' (' + data.fields['year'] + ')' 


   return strc











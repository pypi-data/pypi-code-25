#!/usr/bin/env python

""" 
Merge ``summary.xml`` files from Ganga's subjobs and neatly archive the dir.

Required package LHCB/Kernel/XMLSummaryBase

>> TODO: Check for missing file from subjobs... (a bit tricky...)
"""

import re
import sys
import os
import subprocess
import argparse
import ConfigParser
import logging

from collections import defaultdict
from glob import glob
import xml.etree.cElementTree as ET

## TODO: leave out the outputfile, determine ad-hoc
OUTPUTDIR = 'output'
OUTPUT = 'output/summary.xml' # Name of output file. Use for search in subjob and creation of merged one.

#===============================================================================

class MyFormatter(logging.Formatter):
  """
  https://stackoverflow.com/questions/1343227/can-pythons-logging-format-be-modified-depending-on-the-message-log-level
  """
  err_fmt  = "%(levelname)s!: %(msg)s"
  def format(self, record):
    format_orig = self._fmt
    if record.levelno in (logging.WARNING, logging.ERROR):
      self._fmt = MyFormatter.err_fmt
    # Call the original formatter class to do the grunt work
    result = logging.Formatter.format(self, record)
    # Restore the original format configured by the user
    self._fmt = format_orig
    return result

## Prepare global logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

## Prepare handler
fmt = MyFormatter()
fh = logging.FileHandler('merge.log', 'w')
fh.setLevel(logging.INFO)
fh.setFormatter(fmt)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(fmt)

## add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

#===============================================================================

def get_massstorage_output():
  ## Read the gangarc file, report the masstorage output location if found
  conf = ConfigParser.ConfigParser()
  conf.read(os.path.expandvars("$HOME/.gangarc"))
  ## Return None if it's not set
  if not conf.has_option('Output', 'massstoragefile'):
    return None
  return eval(conf.get('Output', 'massstoragefile'))['uploadOptions']['path']

def init():
  """
  This will do initial check. Namely, we need 'summary' module from LHCb framework.
  Exit if there's no summary library.

  Also create empty dir, for logging.
  TODO: Get the latest
  """
  path = '/sw/lib/lhcb/LHCB/LHCB_v40r0/Kernel/XMLSummaryBase'
  os.environ['XMLSUMMARYBASEROOT'] = path
  sys.path.append(os.environ['XMLSUMMARYBASEROOT']+'/python/XMLSummaryBase')
  try:
    global summary
    import summary
  except ImportError:
    logger.error("Module `summary` from LHCB/LHCB_v36r4/Kernel/XMLSummaryBase not found.")
    sys.exit(-1)

  ## make dir if not exists
  if not os.path.exists(OUTPUTDIR):
    os.makedirs(OUTPUTDIR)

#===============================================================================

def perform_location_check():
  """
  Exit if the location doesn't seem right...
  """
  if re.search(r'/gangadir/workspace/\S+/LocalXML/\d+$',os.getcwd()) is None:
    logger.exception('Bad location, abort: '+ os.getcwd())
    sys.exit(-1)

def perform_existence_precheck():
  """There should be at least 1 summary.xml file, per subjob dir."""
  for sjpath in glob('*/output'):
    if not glob(sjpath+'/summary.xml'):
      logger.warning('No *.xml file found at %s' % sjpath)


#-------------------------------------------------------------------------------

def perform_check_success():
  """Check for tag <success>True/False<success> for individual xml."""
  logger.info('\n### Check <success> in each *.xml')
  all_success = True
  for fpath in glob('*/'+OUTPUT):
    tree    = ET.parse(fpath)
    success = eval(tree.find('success').text)
    all_success &= success
    if not success:
      logger.warning('Found success=False: '+fpath)
  if all_success:
    logger.info('All *.xml found success=True')

#--------------------------------------------------------------

def valid_for_merge(fname):
  """
  Given a file name, return True if it seems like a valid candidate for merging.
  """
  if 'catalog' in fname.lower():
    return False 
  if fname == 'Generatorlogger.xml':
    return False 
  if fname == 'jobDescription.xml':
    return False
  if not fname.endswith('.xml'):
    return False 
  return True

def perform_merge_xml(args):
  logger.info('\n### Perform merging of xml.')

  ## Heuristic search for xml files
  queue = defaultdict(list)
  for dname,_,files in os.walk('.'):
    if dname != os.path.join('.',OUTPUTDIR) and 'input' not in dname: # Relati
      for fname in files:
        if valid_for_merge(fname):
          fullfpath = os.path.join( dname, fname )
          queue[fname].append( fullfpath )

  ## Loop through queue, remove & merge
  logger.info('List of xml merging:')
  for fname,l in queue.iteritems():
    logger.info('{:20} ({} files)'.format(fname, len(l)))
    fout = os.path.join(OUTPUTDIR,fname)
    ## Remove existing one
    if os.path.exists(fout):
      logger.info("Removing existed merge: " + fout)
      os.remove(fout)
    ## Call merge
    summary.Merge(l).write(fout)
  logger.info("Merge completed!")

#-------------------------------------------------------------------------------

def perform_resort():
  """Sort the counter section to be more useful. Do alphabetically for now"""
  logger.info('Sorting: '+OUTPUT)
  tree      = ET.parse(OUTPUT)
  container = tree.find("counters")
  data      = [ (elem.get("name"), elem) for elem in container ]
  data.sort()
  # insert the last item from each tuple
  container[:] = [ item[-1] for item in data ]
  tree.write(OUTPUT)
  logger.info('Sort completed!')


#-------------------------------------------------------------------------------

def perform_merge_ppl():
  """
  If there are __parsedxmlsummary__, merge them all into one,
  so that the subjobs can be archived.
  """
  logger.info('\n### Perform merging of ppl')
  target = 'output/__postprocesslocations__'
  src    = '*/'+target
  ## Check if there's any
  if not glob(src):
    logger.info('No ppl to be merged. Continue.')
    return
  ## Remove existing one
  if os.path.exists(target):
    logger.info("Removing existed merge: " + target)
    os.remove(target)
  ## Easiest to use bash
  arg = 'ls {} | xargs cat | tee {}'.format( src, target)
  subprocess.check_output( arg, shell=True )
  logger.info('Merged ppl completed: %s'%target)

#-------------------------------------------------------------------------------

def perform_jobstatus_check():
  """
  If there are __jobstatus__, do following check.
  > TODO: Assert number check. There should be one of this for each subdir
  - Assert EXITCODE.
  """
  for fpath in glob('*/output/__jobstatus__'):
    with open(fpath) as fin:
      dat = fin.read()
    res = re.findall(r'EXITCODE: (\d+)', dat)
    if not res:
      logger.warning('JobStatus: missing EXITCODE: '+ fpath)
      continue
    code = int(res[0])
    if code != 0:
      logger.warning('JobStatus: failure EXITCODE: '+ fpath)

#-------------------------------------------------------------------------------

def is_slurm():
  ## Check by test the first subjob has `__jobstatus__` file
  ## May be inaccurate
  return os.path.isfile(os.path.join(os.getcwd(),'0/output/__jobstatus__'))

SLURM_FAIL_KEYWORDS = (
  'Application Manager Terminated with error',
  'Traceback (most recent call last)',
  '0x0000000000000000',
)

def perform_slurm_stdout_postcheck():

  def tail(f, n, offset=None):
    """Reads a n lines from f with an offset of offset lines.  The return
    value is a tuple in the form ``(lines, has_more)`` where `has_more` is
    an indicator that is `True` if there are more lines in the file.
    """
    avg_line_length = 74
    to_read = n + (offset or 0)
    while 1:
      try:
        f.seek(-(avg_line_length * to_read), 2)
      except IOError:
        # woops.  apparently file is smaller than what we want
        # to step back, go to the beginning instead
        f.seek(0)
      pos = f.tell()
      lines = f.read().splitlines()
      if len(lines) >= to_read or pos == 0:
        return lines[-to_read:offset and -offset or None], \
          len(lines) > to_read or pos > 0
      avg_line_length *= 1.3

  def readtaildat(path):
    # tail only to have small dat
    with open(path) as fin:
      return tail(fin, 50)[0]
    
  def check_single(path):
    dat = readtaildat(path)
    sjid = path.split('/')[-3]
    if 'stderr' in path and '--- GANGA APPLICATION ERROR END ---' not in dat[-1]:
      logger.warning('{:>4} {}'.format(sjid, dat[-1]))
    for line in dat:
      if any( badword in line for badword in SLURM_FAIL_KEYWORDS ):
        logger.warning('{:>4} {}'.format(sjid, line))

  logger.info('\n### Running SLURM post-check')
  ## check on stdout
  gpath = os.path.join(os.getcwd(), '*/output/std*')
  for path in glob(gpath):
    check_single(path)
  logger.info('SLURM post-check done!')

#--------------------------------------------------------------

def perform_memcheck():
  """Try to determine the largest mem used. For future cluster allocation."""
  logger.info('\n### Memory usage')
  ## V2: Get from xml
  tree   = ET.parse(OUTPUT)
  usage  = float(tree.find("usage").find('stat').text) / 1024
  logger.info('Maximum mem usage: %.2f MB' % usage)


#--------------------------------------------------------------

def extract_lfn(uri):
  """
  >>> extract_lfn('PFN:root://lhcb-sdpd13.t1.grid.kiae.ru.:1094/t1.grid.kiae.ru/data/lhcb/lhcbdisk/lhcb/MC/2012/ALLSTREAMS.DST/00046841/0000/00046841_00000006_2.AllStreams.dst')
  '/lhcb/MC/2012/ALLSTREAMS.DST/00046841/0000/00046841_00000006_2.AllStreams.dst'

  >>> extract_lfn('LFN:root://clhcbdlf.ads.rl.ac.uk//castor/ads.rl.ac.uk/prod/lhcb/LHCb/Collision12/EW.DST/00041836/0000/00041836_00000303_1.ew.dst?svcClass=lhcbDst')
  '/lhcb/LHCb/Collision12/EW.DST/00041836/0000/00041836_00000303_1.ew.dst'

  >>> extract_lfn('PFN:file:///storage/gpfs_lhcb/lhcb/disk/LHCb/Collision12/EW.DST/00041836/0000/00041836_00000303_1.ew.dst')
  '/lhcb/LHCb/Collision12/EW.DST/00041836/0000/00041836_00000303_1.ew.dst'

  >>> extract_lfn('PFN:root://se16.lcg.cscs.ch:1094/pnfs/lcg.cscs.ch/lhcb/lhcb/LHCb/Collision12/EW.DST/00041836/0001/00041836_00018845_1.ew.dst')
  '/lhcb/LHCb/Collision12/EW.DST/00041836/0001/00041836_00018845_1.ew.dst'

  >>> extract_lfn('PFN:root://dcdoor05.pic.es:1094/pnfs/pic.es/data/lhcb/LHCb/Collision12/EW.DST/00041836/0003/00041836_00039307_1.ew.dst')
  '/lhcb/LHCb/Collision12/EW.DST/00041836/0003/00041836_00039307_1.ew.dst'

  >>> extract_lfn('PFN:file:///storage/gpfs_lhcb/lhcb/disk/MC/2012/ALLSTREAMS.DST/00046841/0000/00046841_00000036_2.AllStreams.dst')
  '/lhcb/MC/2012/ALLSTREAMS.DST/00046841/0000/00046841_00000036_2.AllStreams.dst'

  >>> extract_lfn('LFN:/lhcb/MC/2012/ALLSTREAMS.DST/00046841/0000/00046841_00000003_2.AllStreams.dst')
  '/lhcb/MC/2012/ALLSTREAMS.DST/00046841/0000/00046841_00000003_2.AllStreams.dst'

  >>> extract_lfn('PFN:root://lhcb-sdpd16.t1.grid.kiae.ru.:1094/t1.grid.kiae.ru/data/lhcb/lhcbdisk/lhcb/MC/2012/ALLSTREAMS.DST/00046841/0000/00046841_00000003_2.AllStreams.dst')
  '/lhcb/MC/2012/ALLSTREAMS.DST/00046841/0000/00046841_00000003_2.AllStreams.dst'

  >>> extract_lfn('PFN:root://heplnx232.pp.rl.ac.uk:1094/pnfs/pp.rl.ac.uk/data/lhcb/lhcb/MC/2012/ALLSTREAMS.DST/00046841/0000/00046841_00000003_2.AllStreams.dst')
  '/lhcb/MC/2012/ALLSTREAMS.DST/00046841/0000/00046841_00000003_2.AllStreams.dst'

  >>> extract_lfn('PFN:root://bohr3226.tier2.hep.manchester.ac.uk:1094//dpm/tier2.hep.manchester.ac.uk/home/lhcb/lhcb/MC/2012/ALLSTREAMS.DST/00046841/0000/00046841_00000003_2.AllStreams.dst')
  '/lhcb/MC/2012/ALLSTREAMS.DST/00046841/0000/00046841_00000003_2.AllStreams.dst'

  >>> extract_lfn('root://f01-080-125-e.gridka.de:1094/pnfs/gridka.de/lhcb/LHCb/Collision12/EW.DST/00020198/0000/00020198_00000752_1.ew.dst')
  '/lhcb/LHCb/Collision12/EW.DST/00020198/0000/00020198_00000752_1.ew.dst'
  """
  common_endprefix = [ '/data/lhcb/lhcbdisk/lhcb/', '/prod/lhcb/', '/gpfs_lhcb/lhcb/disk/', '/data/lhcb/lhcb/',  '/data/lhcb/', '/home/lhcb/lhcb/', '/lhcb/lhcb/', '/lhcb/' ]
  disposable_nodes = [ 'LFN:', 'PFN:' ]
  #
  uri = uri.replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;") # Escape 
  uri = uri.split('?')[0] # Remove query tail
  for node in disposable_nodes:
    uri = uri.replace(node, '')
  for node in common_endprefix:
    if node in uri:
      # print node, uri
      uri = '/lhcb/'+uri.split(node)[-1]
      break
  return uri

def perform_data_validation(args):
  logger.info("\n### Verifying faulty data in merged output/summary.xml (status!=full)")

  root              = ET.parse(OUTPUT).getroot()
  lfn_nevt          = dict()
  lfn_rawnames      = defaultdict(list)

  ## Check input nodes, collect bad input
  for node in root.find('input').findall('file'):
    rawname = node.get('name')
    lfn     = extract_lfn(rawname)
    nevt    = node.text
    status  = node.get('status')
    valid   = status == 'full' or (not args.partial_is_bad and status in ('part','mult'))
    ## In case of invalid, try to retrieve nevt previous file of same LFN
    ## If there's previous file, this will negate -1.
    if not valid:
      nevt = lfn_nevt.get(lfn, -1)  ## In case of 
    lfn_nevt[lfn] = nevt 
    lfn_rawnames[lfn].append(rawname)

  ## 2nd-pass. Report bad evt
  list_subjob       = list()
  count_input_evt   = 0
  count_output_evt  = 0
  count_bad_files   = 0  
  summary_children  = list(glob('*/output/summary.xml'))
  for lfn,nevt in lfn_nevt.iteritems():
    if nevt <= 0:
      ## This is bad, run through collected rawnames
      count_bad_files += 1
      res_report = defaultdict(list)  # For printout
      logger.warning("Found bad: " + lfn)
      for name in lfn_rawnames[lfn]:
        stdout = subprocess.check_output(['grep', '-r', name] + summary_children)
        sjids  = re.findall(r'(\d+)/output/summary\.xml', stdout)
        list_subjob.extend(sjids)
        ## Print result, group by file
        for line in stdout.strip().split('\n'):
          if line:
            fname,text = line.split(':\t')
            res_report[fname].append(text.strip())
      for fname,l in res_report.iteritems():
        logger.warning(fname)
        logger.warning('\n'.join(l))
      print # line break
    else: # good evt
      count_input_evt += int(nevt)

  ## Check output nodes
  for node in root.find('output').findall('file'):
    count_output_evt += int(node.text)

  # Report
  logger.info('Count input  evt: {:,}'.format(count_input_evt))
  logger.info('Count output evt: {:,}'.format(count_output_evt))
  if count_bad_files==0:
    logger.info("No bad file found. Congrats!")
    return 

  ## Print the command to fix this
  list_subjob = list({ int(sjid) for sjid in list_subjob })
  logger.info("Defected inputdata found....")
  logger.info(sorted(list_subjob))

#--------------------------------------------------------------

def perform_dush():
  ## Report the directory size
  paths = [ os.getcwd() ]  # Default
  jid   = os.getcwd().split('/')[-1]

  ## SKIP due to panfs DOWN on 2015-08-24
  s = get_massstorage_output()
  if s is not None:
    s = os.path.join(s,jid)
    if os.path.exists(s):
      paths.append(s)

  logger.info('\n### Directory size')
  for path in paths:
    size = subprocess.check_output(['du', '-sh', path]).split()[0]
    logger.info('{:5} | {:40}'.format( size, path ))


#===============================================================================

def call_eos(*args):
  """
  Wrapping subprocess.call for eos command from shell. 
  Catching the segfault when there's no token.
  https://stackoverflow.com/questions/22250893

  Return stdout at success, raise `CalledProcessError` otherwise.

  Note: Check with pure 'eos' command, since it yields segfault error code.
  Other subcommand silently crash.

  Usage:
    >> call_eos('ls')
  """
  from subprocess import Popen, PIPE, CalledProcessError, check_output
  cmd     = ['eos'] + list(args)
  proc    = Popen(['eos'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
  out,err = proc.communicate('\n')
  rcode   = proc.returncode
  if rcode != 0: # segfault, 
    raise CalledProcessError( rcode, 'eos' )
  stdout  = check_output(cmd)
  stdout  = stdout.replace('\x1b[?1034h', '')
  return stdout

def perform_hadd():
  """
  Request to call `hadd` on resultant root file , with additional
  lookup on massStorage location (panasas for LPHE).
  """
  logger.info('\n### `hadd` queue')
  logger.info("Seeking root files...")

  ## Prep search location
  paths = [ os.getcwd() ] # By default, the current dir.
  jid   = paths[0].split('/')[-1]

  ## In addition, the massstorage, if any.
  ## SKIP due to panfs DOWN on 2015-08-24
  path2 = get_massstorage_output() 
  if path2 is not None:
    path2 = os.path.join(path2,jid)
    if os.path.exists(path2):
      paths.append( path2 )

  ## Begins the lookup, indexed by filename
  indexed_list = defaultdict(list)
  fulloutdir   = os.path.join(os.getcwd(),OUTPUTDIR)
  for searchpath in paths:
    for dname,_,files in os.walk(searchpath):
      if dname!=fulloutdir:
        for fname in files:
          if fname.endswith('.root'):
            fullfpath = os.path.join( dname, fname )
            indexed_list[fname].append( fullfpath )

  ## Add also EOS, which is not possible to grep like above
  ## Need $EOS_MGM_URL and $EOS_HOME
  if 'EOS_MGM_URL' not in os.environ and 'EOS_HOME' not in os.environ:
    return
  url   = os.environ['EOS_MGM_URL']
  path  = os.path.expandvars('$EOS_HOME/ganga/{}'.format(jid)) # Assume default destination on EOS
  res   = call_eos( 'find', path )
  files = res.split('\n')
  files = res.replace('\x1b[?1034h', '').split('\n') # eos binary produce strange escape code
  for fpath in files:
    if fpath.endswith('.root'):
      fname = os.path.split(fpath)[1]
      indexed_list[fname].append( url+'/'+fpath )

  ## Exit if no queue needed
  if not indexed_list:
    print 'No *.root files found. Ignore hadd.'
    return

  ## Request to user with queue info
  for key,val in indexed_list.iteritems():
    cmd   = ['du', '-shc'] + val
    ## Skip EOS
    if all( 'root://' in arg for arg in val ):
      usage = 0.0
      url   = os.environ['EOS_MGM_URL']
      for arg in val:
        fpath = arg.replace(url, '')
        res   = call_eos( 'ls', '-l', fpath )
        usage += int(res.split()[4]) # Bytes
      # Convert to MB
      usage = '%.2f MB (eos)' % (float(usage)/1024/1024)
    else:
      res   = subprocess.check_output(cmd)
      usage = res.split()[-2]
    logger.info("{:20} ( {} files, {} )".format(key,len(val), usage))
  if raw_input("> Perform hadd? Y/[n]: ") != 'Y':
    return

  ## Perform upon request
  for fname, queue in indexed_list.iteritems():
    target = 'output/%s'%fname
    ## Check existing file, ask for permission to delete
    if os.path.exists(target):
      if raw_input("Output existed, remove it? Y/[n]: ") == 'Y':
        subprocess.call(['rm', target])
      else:
        logger.info("Retain existing file, continue.")
    ## Do actual merge
    cmd = [ 'hadd', target ] + sorted(queue) # '-f9',
    subprocess.call(cmd)

#-------------------------------------------------------------------------------

def perform_delete_subjobs_root():
  """
  Ask user to delete *.root files ONLY of the subjobs.
  ask before performing archive (where no data is delete).
  """
  ## Check first how many are there. Skip if there is None
  res1 = glob('*/input/*.root')
  res2 = glob('*/output/*.root')
  res  = res1+res2
  if not res:
    return
  if raw_input('\n> Delete *.root files (%i) of subjobs? Y/[n]: '%len(res)) != 'Y':
    return
  cmd = 'rm -f */output/*.root */input/*.root'
  logger.info('Running: %r'%cmd)
  subprocess.call(cmd, shell=True)
  logger.info('Delete successfully!')

#-------------------------------------------------------------------------------

searchpath = [
  'output/*.root',
  'output/*.dst',
  '*/output/*.dst',
  'output/*.sim',
  '*/output/*.sim',
  'output/*.digi',
  '*/output/*.digi',
]

def perform_eoscp():
  """
  Ask to upload the large data to EOS. Can be either from main or subjobs.
  """
  queue = []
  for path in searchpath:
    queue += glob(path)
  ## Exit immediately if there's nothing to do
  if not queue:
    return 
  ## Ask for permission
  logger.info('\n### Upload large files to EOS')
  logger.info('Found files: %i'%len(queue))
  if raw_input("Perform upload to EOS? Y/[n]: ") != 'Y':
    return 
  assert 'EOS_MGM_URL' in os.environ, 'Needs $EOS_MGM_URL defined.'
  assert 'EOS_HOME' in os.environ, 'Needs $EOS_HOME defined.'
  jid = os.getcwd().split('/')[-1]
  for src in queue:
    target  = os.path.join('$EOS_MGM_URL/$EOS_HOME/ganga', jid, src)
    target  = os.path.expandvars(target.replace('output/',''))
    args    = 'eoscp', '-s', src, target
    stdout  = subprocess.check_output(args)
    logger.info(stdout.strip())
  logger.info('All files uploaded to EOS successfully')
  if raw_input("Delete those files locally? Y/[n]: ") != 'Y':
    return 
  args = ['rm'] + queue
  subprocess.call(args)



#-------------------------------------------------------------------------------

def perform_archive():
  """
  (Experimental) Archive the subjobs into single data.tar.zx, and delete them.
  """
  if raw_input("\n> Perform archive? Y/[n]: ") != 'Y':
    return

  ## Check is already existed, do nothing otherwise (not delete!).
  target = 'data.tar.xz'
  if os.path.exists(target):
    logger.warning('Found existing archive (%s). Abort for safety'%target)
    return
  cmd = "tar -Jcf {0} --exclude='./output' --exclude={0} .".format(target)
  subprocess.call(cmd, shell=True)
  cmd = "find . -maxdepth 1 -type d -name '[0-9]*' | xargs rm -rf ; rm -rf debug/ input/"
  subprocess.call(cmd, shell=True)
  logger.info('Archiving finished succesfully: %r'%target)

#===============================================================================

def main(args):
  init()
  perform_location_check()

  perform_dush()
  perform_existence_precheck()
  perform_check_success()
  perform_merge_xml(args)
  perform_resort()
  perform_merge_ppl()
  perform_jobstatus_check()
  if is_slurm():
    perform_slurm_stdout_postcheck()
  perform_memcheck()
  if not args.skip_validate:
    perform_data_validation(args)

  perform_hadd()
  perform_delete_subjobs_root()
  perform_eoscp()
  perform_archive()
  print # endline

#===============================================================================

if __name__ == '__main__':
  ## Read args
  parser = argparse.ArgumentParser()
  parser.add_argument('-p', '--partial-is-bad', action="store_true", default=False, help="If True, consider 'partial' data as false too.")
  parser.add_argument('-s', '--skip-validate',  
                        action="store_true", 
                        default=False, 
                        help="If not skip, the script will loop check whether all data input has been correctly processed or not.")
  parser.add_argument('--hadd', action='store_true', default=False,
                      help="If True, run directly the `hadd` module.")
  parser.add_argument('--archive', action='store_true', default=False,
                      help="If True, run directly the `archive` module")

  # parser.add_argument('-n', '--files', type=int, help='Max number of files to merge', default=-1)
  args = parser.parse_args()

  ## Run only hadd module.
  if args.hadd:
    perform_hadd()
    sys.exit()

  if args.archive:
    perform_archive()
    sys.exit()

  main(args)

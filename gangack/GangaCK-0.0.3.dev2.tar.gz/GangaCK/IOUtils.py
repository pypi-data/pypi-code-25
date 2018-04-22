
import os
import re
import math
import zlib
import xml.etree.ElementTree as ET
from PythonCK.ioutils import dump_to_file
from PythonCK.itertools import EnumContainer, chunks, flatten
from PythonCK.decorators import cache_to_file
from . import GPI, logger, IS_GANGA61

__all__ = ()  # No need to export things externally.

UriType = EnumContainer( 'PFN', 'LFN', 'BKQ', 'XML' )

## For uri identifier
WHITELIST_BKQ_PREFIX = (
  'evt:',
  'sim:',
  'evt+std:',
  'sim+std:',
)

#==============================================================================
# UTILS
#==============================================================================

def checksum_adler32(filepath):
  """
  Note: Used in Dirac / Ganga as default checksum protocol.

  Args:
    filepath (str): Path to local file for checksum test.

  Return
    string of checksum, with '0x' prefix removed.

  Usage:

    >>> checksum_adler32('tests/res/r197/data')
    '77e77c10'

  """
  with open(filepath) as fin:
    dat1 = fin.read()
  return hex(zlib.adler32(dat1) & 0xFFFFFFFF)[2:]  # Exclude the 0x part

#==============================================================================
# BKQUERY URI OPERATION
#==============================================================================

def _parser_remove_evtnickname(uri):
  """
  Simply remove the nickname bit from BKQ-uri

  Usage:
    >>> _parser_remove_evtnickname('/path/12345678 ( nickname )/DST')
    '/path/12345678/DST'

  """
  return re.sub(r'\s\( .* \)', '', uri)

def _parser_uri_evt(uri):
  """
  Handle the evt-style uri to std-style. Need to swap the evtnumber to the back.
  Also kill the subprocess nickname from uri.

  Note: The function assume that the input is valid evt+std string.

  Usage: 
    >>> _parser_uri_evt('/MC/Dev/30000000 ( minbias )/.../XDIGI')
    '/MC/Dev/.../30000000/XDIGI'

  """
  uri   = _parser_remove_evtnickname(uri)
  code  = re.findall(r'/(\d{8})/',uri)[0]
  l     = uri.split('/')
  l.pop(l.index(code)) # Remove from original list
  l.insert(-1, code) # Insert just one-block before last one.
  return '/'.join(l)


def parse_bkq_uri(uri):
  """
  Format arbitary BKQ-uri into standard one, compatible with `BKQuery.getDataset` call.

  ## Idempotent
  
  >>> parse_bkq_uri('/MC/Dev/Beam6500GeV-RunII-MagDown-Nu1.5-25ns-Pythia8/Sim08e/30000000/XDIGI')
  '/MC/Dev/Beam6500GeV-RunII-MagDown-Nu1.5-25ns-Pythia8/Sim08e/30000000/XDIGI'

  ## Old-style
  
  >>> parse_bkq_uri('evt://MC/Dev/30000000 ( minbias )/Beam6500GeV-RunII-MagDown-Nu1.5-25ns-Pythia8/Sim08e/XDIGI')
  '/MC/Dev/Beam6500GeV-RunII-MagDown-Nu1.5-25ns-Pythia8/Sim08e/30000000/XDIGI'
  
  >>> parse_bkq_uri('evt://MC/Dev/30000000/Beam6500GeV-RunII-MagDown-Nu1.5-25ns-Pythia8/Sim08e/XDIGI')
  '/MC/Dev/Beam6500GeV-RunII-MagDown-Nu1.5-25ns-Pythia8/Sim08e/30000000/XDIGI'
  
  >>> parse_bkq_uri('sim://MC/Dev/Beam6500GeV-RunII-MagDown-Nu1.5-25ns-Pythia8/Sim08e/30000000 ( minbias )/XDIGI')
  '/MC/Dev/Beam6500GeV-RunII-MagDown-Nu1.5-25ns-Pythia8/Sim08e/30000000/XDIGI'
  
  >>> parse_bkq_uri('evt://MC/2012/42100000/Beam4000GeV-2012-MagDown-Nu2.5-Pythia8/Sim08a/Digi13/Trig0x409f0045/Reco14a/Stripping20NoPrescalingFlagged/ALLSTREAMS.DST')
  '/MC/2012/Beam4000GeV-2012-MagDown-Nu2.5-Pythia8/Sim08a/Digi13/Trig0x409f0045/Reco14a/Stripping20NoPrescalingFlagged/42100000/ALLSTREAMS.DST'

  ## New-style
  
  >>> parse_bkq_uri('sim+std://MC/2012/Beam4000GeV-JulSep2012-MagUp-Nu2.5-EmNoCuts/Sim06b/Trig0x40990042Flagged/Reco14/Stripping20NoPrescalingFlagged/42311002/ALLSTREAMS.DST')
  '/MC/2012/Beam4000GeV-JulSep2012-MagUp-Nu2.5-EmNoCuts/Sim06b/Trig0x40990042Flagged/Reco14/Stripping20NoPrescalingFlagged/42311002/ALLSTREAMS.DST'

  >>> parse_bkq_uri('evt+std://MC/Dev/49000153/Beam6500GeV-RunII-MagDown-Nu1.6-25ns-Pythia8/Sim08f/Reco15DEV/LDST')
  '/MC/Dev/Beam6500GeV-RunII-MagDown-Nu1.6-25ns-Pythia8/Sim08f/Reco15DEV/49000153/LDST'

  ## New-style evt: Real

  >>> parse_bkq_uri('evt+std://LHCb/Collision12/90000000/Beam4000GeV-VeloClosed-MagUp/Real Data/Reco14/Stripping21/EW.DST')
  '/LHCb/Collision12/Beam4000GeV-VeloClosed-MagUp/Real Data/Reco14/Stripping21/90000000/EW.DST'

  ## Missing Digi

  >>> parse_bkq_uri('evt+std://MC/2012/42311002/Beam4000GeV-JulSep2012-MagDown-Nu2.5-EmNoCuts/Sim06b/Trig0x40990042Flagged/Reco14/Stripping20NoPrescalingFlagged/ALLSTREAMS.DST')
  '/MC/2012/Beam4000GeV-JulSep2012-MagDown-Nu2.5-EmNoCuts/Sim06b/Trig0x40990042Flagged/Reco14/Stripping20NoPrescalingFlagged/42311002/ALLSTREAMS.DST'

  ## Bad

  >>> parse_bkq_uri('/lhcb/user/c/ckhurewa/2014_11/90521/90521704/Bender_e_h3.dst')
  Traceback (most recent call last):
  ...
  ValueError: ...

  """

  ## May already formatted...
  if uri.startswith('/MC/') or uri.startswith('/LHCb/'):
    return uri
  ## Order is correct, just need to trim & remove event-nickname
  if uri.startswith('sim://'):
    return _parser_remove_evtnickname(uri.replace('sim://', '/'))
  if uri.startswith('sim+std://'):
    return _parser_remove_evtnickname(uri.replace('sim+std://', '/'))
  ## New format
  if uri.startswith('evt+std://'):
    return _parser_uri_evt(uri.replace('evt+std://', '/'))
  if uri.startswith('evt://'):
    return _parser_uri_evt(uri.replace('evt://', '/'))
  raise ValueError('Unknown format: %r'%uri)


@cache_to_file(timeout=60*60*24*30, input_skip_write=None) #, output_skip_write=False)
def get_raw_list_LFN(uri):
  """
  Given the LHCb-bookkeeping uri, return list of string represent LFNs names.
  """
  logger.info('Resolving uri BKQ -> LFNs: %r'%uri)
  files = GPI.BKQuery(parse_bkq_uri(uri)).getDataset().files 
  if not files:
    raise ValueError("Found null LFNs from given uri. Perhaps uri is wrong, check me!")
  if IS_GANGA61:
    return sorted([ str(lfn.lfn) for lfn in files ])
  else:
    return sorted([ str(lfn.name) for lfn in files ])


#==============================================================================
# OFFLINE LOCAL OPERATION
#
# offline means there's no need to invoke Ganga.GPI interface...
#==============================================================================

def extract_lfn_from_ppl(ppl_file):
  """
  Given a path to `__postprocesslocations__ file`, extract the output 
  lfn inside.

  >>> extract_lfn_from_ppl('tests/res/__postprocesslocations__')
  ['/lhcb/user/c/ckhurewa/2014_11/90521/90521704/Bender_mu_mu.dst', '/lhcb/user/c/ckhurewa/2014_11/90521/90521704/Bender_e_h3.dst']

  """
  logger.debug('ppl: '+ppl_file)
  with open(ppl_file) as fin:
    res = re.findall(r'->(.*):::\[', fin.read())
  for obj in res:
    logger.debug('-->: %r'%obj)
  return res

def extract_eos_from_ppl(ppl_file):
  """
  Same as above, for list of EOS files.
  """
  logger.debug('ppl: '+ppl_file)
  with open(ppl_file) as fin:
    res = re.findall(r'massstorage \S+ (/eos/\S+)', fin.read())
  for obj in res:
    logger.debug('-->: %r'%obj)
  return res


#==============================================================================
# REMOTE LFN OPERATION
#==============================================================================

def lfn_abspath(path=''):
  """
  Return absolute LFN path, starting from user's home dir by default.

  Usage:
    >>> getfixture('testuser')
    >>> lfn_abspath('myfile.dst')
    '/lhcb/user/t/testuser/myfile.dst'
    
    >>> lfn_abspath('LFN:myfile.dst')
    '/lhcb/user/t/testuser/myfile.dst'

    >>> lfn_abspath()
    '/lhcb/user/t/testuser'

    >>> lfn_abspath('/already/absolute/path')
    '/already/absolute/path'

  """

  if path.startswith('LFN:'):
    path = path.replace('LFN:','')
  if path.startswith('/'):  # Already absolute, do nothing
    return path
  dpath = GPI.config.DIRAC.DiracLFNBase
  if not path:
    return dpath
  return os.path.join(dpath, path)

def lfn_put(path_source, destination_dir=None):
  """
  Helper method to upload the given file to LFN location,
  
  Args:
    path_source (str): Absolute path to local file to upload.

    destination_dir (str): Directory path on remote to put this LFN.
                           If None, default to home dir.

  Return:
    String LFN-path to uploaded file (without 'LFN:' prefix),
    return None if the operation fails.

  Usage:
    >>> getfixture('dirac_success')
    >>> lfn_put( '/local/path/to/file.root' )
    '/lhcb/user/t/testuser/file.root'
    >>> lfn_put( '/local/path/to/file.root', destination_dir='/remote/path' )
    '/remote/path/file.root'

  """

  logger.info("Updating: %s" % path_source)
  filedir, filename  = os.path.split(path_source)
  if destination_dir is None:
    destination_dir = lfn_abspath()  # Home
  path_dest = os.path.join(destination_dir, filename)
  d_old     = GPI.DiracFile(lfn=path_dest)
  logger.info(">  Checking metadata...")
  if d_old.getMetadata()['Value']['Successful']:
    logger.info(">  Old file existed, removing...")
    d_old.remove()
  d_new = GPI.DiracFile(namePattern=filename, localDir=filedir, lfn=path_dest)
  logger.info(">  Putting updated file...")
  d_new.put()
  metadata = d_new.getMetadata()
  logger.info(metadata)
  if metadata['Value']['Failed']: 
    logger.warning("Failed to put file: " + path_source)
    return None
  return path_dest

def lfn_checksum(lfn):
  """
  Given a LFN-path, try to return its checksum value, which already reside
  in its metadata.

  Args:
    lfn (string): Path to remote file.

  Usage:
    >>> getfixture('dirac_success')
    >>> lfn_checksum( 'somefile.root' )
    'fba3a47f'

  """
  lfn  = lfn_abspath(lfn)
  dat2 = GPI.DiracFile(lfn=lfn).getMetadata()
  return None if dat2['Value']['Failed'] else dat2['Value']['Successful'][lfn]['Checksum']


def is_LFN_uptodate(localfile, lfn):
  """
  Return True if the lfn is up-to-date against check with local file. 
  Use Adler32 check on DiracFile

  If lfn path is relative, check based on user's home dir.
  (from config.DiracLFNBase)

  """
  logger.info('Checking: %r'%lfn)
  ## Get local's and remote's
  cs1 = checksum_adler32(localfile)
  cs2 = lfn_checksum(lfn)
  ## Compare!
  logger.debug('checksum1: %r'%cs1)
  logger.debug('checksum2: %r'%cs2)
  return cs1==cs2 


#==============================================================================
# CATALOGUE CACHER
#==============================================================================

def rawxml_patch_gpfs(rawxmlentry):
  """
  Provide the accessURL patch on data stored at CNAF with file:/ protocol

  >>> rawxml_patch_gpfs('<pfn filetype="ROOT_All" name="file:///storage/gpfs_lhcb/lhcb/disk/LHCb/Collision12/EW.DST/00020241/0000/00020241_00000210_1.ew.dst" />')
  '<pfn filetype="ROOT_All" name="root://xrootd-lhcb.cr.cnaf.infn.it//storage/gpfs_lhcb/lhcb/disk/LHCb/Collision12/EW.DST/00020241/0000/00020241_00000210_1.ew.dst" />'

  ## Do nothing if not relevant.
  >>> rawxml_patch_gpfs('<pfn filetype="ROOT_All" name="root://f01-080-123-e.gridka.de:1094/pnfs/gridka.de/lhcb/LHCb/Collision12/EW.DST/00020241/0000/00020241_00000210_1.ew.dst" />')
  '<pfn filetype="ROOT_All" name="root://f01-080-123-e.gridka.de:1094/pnfs/gridka.de/lhcb/LHCb/Collision12/EW.DST/00020241/0000/00020241_00000210_1.ew.dst" />'
  """
  return rawxmlentry.replace('file:///storage/gpfs_lhcb/', 'root://xrootd-lhcb.cr.cnaf.infn.it//storage/gpfs_lhcb/')

def _rawxml_parser(rawxml):
  """
  Given a rawxml string from getCatalog, return new dict with that data indexed
  by lfn name. Header content is stripped, only individual entry will be returned.

  Since this will be used as primary parser for catalog resoluation, provide the 
  necessary patches here.

  """

  root = ET.fromstring(rawxml)
  res = {f.find('logical').find('lfn').get('name'):ET.tostring(f).strip() for f in root}
  ## Patch for CNAF (-o /Resources/StorageElements/DefaultProtocols=root)
  for lfn,entrystr in dict(res).iteritems():
    res[lfn] = rawxml_patch_gpfs(entrystr)
  ## Finally
  return res


@cache_to_file(timeout=60*60*24*30, input_skip_write=None)
def get_catalog_lfn(lfn):
  """Give a single LFN uri, return its correspondent entry in XMLcatalogger.""" 
  ds     = GPI.LHCbDataset([ 'LFN:'+lfn.replace('LFN:', '') ])
  rawxml = ds.getCatalog()
  dat    = _rawxml_parser(rawxml)
  assert len(dat)==1, 'Bad getCatalog'
  return dat.values()[0].strip()  # Interest only in xmlstr entry


@cache_to_file(timeout=60*60*24*30, input_skip_write=None)
def get_catalog_bkq(uri):
  """
  Delegate its work to `get_catalog_lfn`
  Careful with usage of this guy. Without `early_giveup` and if >10 LFN doesn't
  have the cache in `get_catalog_lfn`, this may take ages...
  
  For coherence, this guy will abort if any children lfn has missing catalog
  """
  
  logger.info('Queueing catalogue for: %r'%uri)
  entries = [ get_catalog_lfn(lfn, early_giveup=True) for lfn in get_raw_list_LFN(uri) ]
  ## If there's ANY missing catalog, abort for atomic-integrity.
  if None in entries:  # Since I do check midway, cannot use generator in expr above
    logger.warning("Some lfn has missing cache, return None. (for performance reason, don't dive deeper).")
    return None
  ## Provide also a patch here (since I dont have to recache lfn level immediately)
  entries = ( rawxml_patch_gpfs(e) for e in entries )
  ## Finally
  return ''.join(entries)


def has_workers_running(name='idle'):
  ## Simply return number of non-idle working nodes.
  return any(s==name for _,s,_ in GPI.queues._user_threadpool.worker_status())

def split_queues(nqueue):
  """
  Return tuple (size-per-batch, nbatch) suitable for ganga-queues splitting.
  Try to skew toward more queues of smaller size.

  >>> split_queues(4)
  (1, 4)
  >>> split_queues(10)
  (1, 10)
  >>> split_queues(20)
  (2, 10)
  >>> split_queues(100)
  (3, 34)

  """
  size    = 1 if nqueue <= 10 else min(max( 1, int(round(nqueue**0.2))), 20 )  # Cap by sqrt of nqueue, min 1, max 20. (if <= 5, use all queue )
  nbatch  = int(math.ceil( 1. * nqueue / size ))
  return size,nbatch

def _cache_catalog_lfns(lfns):
  """
  Give a list of lfns, expect the path to (create-on-demand) xmlcatalogger.
  This is the only method that handles the heavy work duties, so USE WITH CARE!
  This will NOT return any result, it will just push the result into 
  cache of `get_catalog_lfn`.

  >>> _cache_catalog_lfns('bare_string_not_accepted')
  Traceback (most recent call last):
  ...
  AssertionError

  >>> _cache_catalog_lfns([ 123, 'need_all_string', 45.6 ])
  Traceback (most recent call last):
  ...
  AssertionError

  """

  ## Check. I don't want to pollute cache engine
  assert isinstance(lfns, list)
  assert all(isinstance(s, basestring) for s in lfns)

  # @cache_to_file(timeout=60*60*24) # 1day cache, very rawdat, dev only
  def lfns_catalog_raw(lfns):
    ds = GPI.LHCbDataset([ 'LFN:'+s.replace('LFN:', '') for s in lfns ])
    try:
      return ds.getCatalog()
    except Exception, e:
      logger.exception(e)
      logger.warning('Failed to retrive following LFNs:')
      for lfn in lfns:
        logger.warning(lfn)
      
  def noderun_raw_getCatalog(i, nbatch, lfns):
    ## Wrapped version for GPI.queues.add, hold the log, cache at inner call.
    msg ='GetCatalog batch %d/%d' % (i+1,nbatch)
    logger.info(msg + ' : Start')
    rawxml = lfns_catalog_raw(lfns)
    if rawxml is None:
      logger.info(msg + ' : aborted')
      return
    rawdat = _rawxml_parser(rawxml)
    ## Add cache into repo
    for lfn,entry in rawdat.iteritems():
      key = get_catalog_lfn.makekey(lfn)
      get_catalog_lfn[key] = entry
    logger.info(msg + ' : Done!')

  ## Filter missing one more time, reduce the load (as well as standalone usage)
  list_queue = [ lfn for lfn in lfns if get_catalog_lfn(lfn, early_giveup=True) is None ]
  if not list_queue:  # Exit if there's nothing left to do
    logger.info('All caches are in place [%d], exit successfully.' % len(lfns))
    return 

  ## Prefer to abort if there's no working queue available (in case prefetching is still ongoing)
  if has_workers_running(name='noderun_raw_getCatalog'):
    logger.warning("Abort, to prevent flood of duplicate queue, try again when there's queue available...")
    return

  ## Deploy the remote calls and cache (by lfns) the raw results.
  ## Split queue into chunks of 20 (large enough so I may ctrl-d break in-between)
  nqueue      = len(list_queue)
  SIZE,nbatch = split_queues(nqueue)
  logger.info('LHCbDataset.getCatalog, please wait... size = %d / %d --> %d batches'%(nqueue,SIZE,nbatch))
  for i,lfns in enumerate(chunks( list_queue, SIZE )):
    GPI.queues.add( noderun_raw_getCatalog, args=(i,nbatch,lfns))



#==============================================================================
# File Interfaces
#==============================================================================

def PhysicalFile__remove(self):
  pass


#==============================================================================
# LHCbDataset
#==============================================================================


_msg_1stpass_warning = """

LHCbDataset.new found list of lfns pending for 1st-pass catalog-caching.
size = %d

Because prefetching may take a long time, it will be done under Ganga's 
non-callbacking `queue.add` multiprocessing, and the LHCbDataset.new 
call will be terminated with Exception at the end. Don't be panic.
(Raise exepeion, in case this call is invoked inside submission script).

If prefetch is ready, you'll not see this msg again.

Flush the queue to background for prefetching? Y/[n]
"""

XMLTEMPLATE = """<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<!-- Edited By PoolXMLCatalogger.py -->
<!DOCTYPE POOLFILECATALOG SYSTEM "InMemory">
<POOLFILECATALOG>
{}
</POOLFILECATALOG>
"""

def homogenize_inputs(*args):
  """
  Support method for Part-I of LHCbDataset.new
  Disect different kind of inputs into a list of string + any mapping(lfn->pfn) provided

  >>> homogenize_inputs('/some/string')
  (['/some/string'], [])

  ## In case of missing file, acknowledge, but keep going.
  >>> homogenize_inputs('tests/res/NON_EXISTENT.py')
  ([], [])

  ## known from .py extension
  >>> for x in homogenize_inputs('tests/res/inputdata.py')[0]:
  ...   print(x)
  root://eoslhcb.cern.ch//eos/lhcb/user/r/rvazquez/DSTsForS23/114088641_NoBias_2015_0xEE63_Hlt.dst
  root://eoslhcb.cern.ch//eos/lhcb/user/r/rvazquez/DSTsForS23/114088646_NoBias_2015_0xEE63_Hlt.dst
  root://eoslhcb.cern.ch//eos/lhcb/user/r/rvazquez/DSTsForS23/114088652_NoBias_2015_0xEE63_Hlt.dst

  ## Bad
  >>> homogenize_inputs(None)
  Traceback (most recent call last):
  ...
  ValueError: ...

  """
  queue_raw   = []
  xml_entries = []  # list of xmlentries, single node per lfn.
  for arg in flatten(args):  # Need some flatten in case arg is glob
    logger.debug( 'Checking: %r' % arg )

    if isinstance(arg, basestring): # Single string --> (LFN,PFN,BKQ single uri) OR (path to script.py)
      ## expand local envvar first
      arg = os.path.expandvars(arg).strip()
      if arg.endswith('.py'):  # Gaudipython script, expect IOHelper style input
        try:
          with open(arg) as fin:
            dat = fin.read()
          raw = re.findall(r"IOHelper\(.*\)\.inputFiles\((\[.*\]).*\)", dat, re.DOTALL)[0]
          queue_raw.extend( eval(raw) )  # Expect this to be a eval-ready stringified-list
          ## TODO: Extract path to catalogue from .py file (e.g., stripping)
          # xml = re.findall(r'FileCatalog()\.Catalogs \+= (\[.*\])', dat, re.DOTALL)
        except Exception, e:
          logger.exception(e)
          logger.warning('Failed to parse script file, skip: %s' % arg)
          continue
      else:  # Bare single-uri input
        queue_raw.append( arg )

    elif isinstance( arg, file ):     # Local file, parse each line individually
      queue_raw.extend( arg.read().splitlines() )

    elif isinstance( arg, GPI.Job ):      # Job instance --> Take all its outputs (LFN+PFN)
      ## TODO: Should extract out both PFN/LFN files, all, including new G6.1 compat
      queue_raw.extend(sorted([ lfn for lfn in arg.lfn_list() if _supported(lfn) ]))

    elif isinstance( arg, GPI.LHCbDataset ):      
      ## LHCbDataset instance. 
      # extend the list of file, as well as extract the contents inside xml
      for f in arg.files:
        if isinstance( f, GPI.DiracFile ):
          queue_raw.append( 'LFN:'+f.lfn )
        elif isinstance( f, GPI.LogicalFile ):
          queue_raw.append( f.name )
        elif isinstance( f, GPI.File ):
          queue_raw.append( f.name )
        else:
          raise NotImplementedError
      xmlfile = arg.XMLCatalogueSlice
      if xmlfile: 
        name = None
        if isinstance(xmlfile, GPI.LocalFile):
          name = xmlfile.namePattern 
        elif isinstance(xmlfile, GPI.File ):
          name = xmlfile.name 
        if name:
          with open(xmlfile.name) as fin:
            rawxml = fin.read()
          xml_entries.extend( _rawxml_parser(rawxml).values() )

    else:
      raise ValueError('Unknown type of input: %r'%type(arg))
  return queue_raw, list(set(xml_entries))

  ### >>> Dirty integration for `readInputData`


def uri_identifier(s):
  """

  LIST OF URI TYPES
  -----------------

  BKQ-type (Bookeeping Query):

    >>> uri_identifier('evt+std://MC/Beam6500GeV/LDST')
    ('BKQ', 'evt+std://MC/Beam6500GeV/LDST')


  PFN-type (Physical file):

    In case of PFN, the 'PFN:' prefix will be add which is needed by 
    (pre-6.1 Ganga) LHCbDataset constructor. 

    >>> uri_identifier('root://file.dst')
    ('PFN', 'PFN:root://file.dst')

    EOS-path is similar to LFN-type, but the 'access url' can be resolved 
    deterministically into PFN-type.

    >>> uri_identifier('/eos/lhcb/user/x/xxx/file.dst')
    ('PFN', 'PFN:root://eoslhcb.cern.ch//eos/lhcb/user/x/xxx/file.dst')


  LFN-type (Logical file):

    LFN-style uri will be send to `_cache_catalog_lfns` in order to prepare 
    the catalog cache, otherwise it'll be send to LHCbDataset constructor.

    >>> uri_identifier('/lhcb/something.ldst')
    ('LFN', '/lhcb/something.ldst')

  XML-type (Usually path to catalogger.xml file): 

    This is somewhat intermediate between PFN+LFN. It's partly PFN because of 
    the list of direct-accessURL inside, but also partly LFN since they belong
    to the same file but just provided for fallback.

    >>> uri_identifier('something.xml')
    ('XML', 'something.xml')

  Args:
    s (str): Input uri to be identified.

  Return:
    Tuple ( UriType , str ): 
      str is same as input, but nicely formatted for its respective uri type. 

  DOCTEST:

    ## PFN
    >>> uri_identifier('PFN:/file.dst')
    ('PFN', 'PFN:/file.dst')
    >>> uri_identifier('root://file.dst')
    ('PFN', 'PFN:root://file.dst')
    >>> uri_identifier('file:///storage/gpfs_lhcb/lhcb/disk/MC/Dev/LDST/00041927/0000/00041927_00000002_1.ldst')
    ('PFN', 'PFN:root://xrootd-lhcb.cr.cnaf.infn.it//storage/gpfs_lhcb/lhcb/disk/MC/Dev/LDST/00041927/0000/00041927_00000002_1.ldst')
    >>> uri_identifier('/storage/gpfs_lhcb/lhcb/disk/MC/Dev/LDST/00041927/0000/00041927_00000002_1.ldst')
    ('PFN', 'PFN:root://xrootd-lhcb.cr.cnaf.infn.it//storage/gpfs_lhcb/lhcb/disk/MC/Dev/LDST/00041927/0000/00041927_00000002_1.ldst')
    >>> uri_identifier('/panfs/khurewat/MC/H2AA_H125_A30/8TeV_nu2.5_md100/Bender/2358/0/output/Bender.dst')
    ('PFN', 'PFN:/panfs/khurewat/MC/H2AA_H125_A30/8TeV_nu2.5_md100/Bender/2358/0/output/Bender.dst')

    ## LFN
    >>> uri_identifier('LFN:/file.dst')
    ('LFN', '/file.dst')
    >>> uri_identifier('castor://clhcbstager.ads.rl.ac.uk:9002/?svcClass=lhcbDst&path=/castor/ads.rl.ac.uk/prod/lhcb/MC/Dev/LDST/00041927/0000/00041927_00000001_1.ldst')
    ('LFN', '/lhcb/MC/Dev/LDST/00041927/0000/00041927_00000001_1.ldst')
    >>> uri_identifier('/castor/ads.rl.ac.uk/prod/lhcb/MC/Dev/LDST/00041927/0000/00041927_00000001_1.ldst')
    ('LFN', '/lhcb/MC/Dev/LDST/00041927/0000/00041927_00000001_1.ldst')
    >>> uri_identifier('/lhcb/MC/Dev/LDST/00041927/0000/00041927_00000002_1.ldst')
    ('LFN', '/lhcb/MC/Dev/LDST/00041927/0000/00041927_00000002_1.ldst')

    ## BKQ
    >>> uri_identifier('evt://MC/2012/42100000/Beam4000GeV-2012-MagDown-Nu2.5-Pythia8/Sim08a/Digi13/Trig0x409f0045/Reco14a/Stripping20NoPrescalingFlagged/ALLSTREAMS.DST')
    ('BKQ', 'evt://MC/2012/42100000/...)
    >>> uri_identifier('evt+std://LHCb/Collision12/90000000/Beam4000GeV-VeloClosed-MagDown/Real Data/Reco14/Stripping21/EW.DST')
    ('BKQ', 'evt+std://LHCb/Collision12/90000000/...)

    ## Bad
    >>> uri_identifier(None)
    Traceback (most recent call last):
    ...
    ValueError: ...

    ## Unidentified
    >>> uri_identifier('UNIDENTIFIED')
    ('PFN', 'UNIDENTIFIED')
    >>> uri_identifier('/MC/Dev/Beam6500GeV-RunII-MagDown-Nu1.5-25ns-Pythia8/Sim08e/30000000/XDIGI')
    ('PFN', '/MC/Dev/Beam6500GeV-RunII-MagDown-Nu1.5-25ns-Pythia8/Sim08e/30000000/XDIGI')

  """

  ## Early reject if it's not a string
  if not isinstance(s, basestring): 
    raise ValueError('Bad uri type: '+str(type(s)))

  ## BKQs ( just identify, don't format. Delegate it to parse_bkq_uri)
  utype = UriType.BKQ 
  if any( s.startswith(prefix) for prefix in WHITELIST_BKQ_PREFIX ):
    return utype, s

  ## XML ( string, path to xml file )
  utype = UriType.XML
  if s.endswith('.xml'):
    return utype, s

  ## PFNs: Immediately put PFN: prefix in front
  utype = UriType.PFN
  if s.startswith('PFN:'):
    return utype, s    
  if s.startswith('root:'):
    return utype, 'PFN:'+s
  if s.startswith('file:///storage') or s.startswith('/storage'):  # CNAF internal protocol
    # file:///storage/gpfs_lhcb/lhcb/disk/MC/Dev/LDST/00041929/0000/00041929_00000002_1.ldst
    # CONSTRUCT MANUALLY - EXPERIMENTAL!
    return utype, 'PFN:root://xrootd-lhcb.cr.cnaf.infn.it/'+re.findall(r'(/storage/\S+)', s)[0]
  if s.startswith('/panfs/khurewat') or s.startswith('/home/khurewat/'): # It's my file
    return utype, 'PFN:'+s
  if os.path.isfile(s)  :  # If it's local file
    return utype, 'PFN:'+s
  ## eos subtype can be treated as PFN easily
  if s.startswith('/eos/lhcb/'):
    return utype, 'PFN:root://eoslhcb.cern.ch/'+s
  if s.startswith('/eos/'):
    raise NotImplementedError

  ## LFNs: Don't put LFN: yet, to be resolved later
  utype = UriType.LFN
  if s.startswith('LFN:'):
    return utype, s.replace('LFN:','')
  if s.startswith('castor:') or s.startswith('/castor'):
    # castor://clhcbstager.ads.rl.ac.uk:9002/?svcClass=lhcbDst&path=/castor/ads.rl.ac.uk/prod/lhcb/MC/Dev/LDST/00041929/0000/00041929_00000001_1.ldst
    return utype, re.findall(r'(/lhcb/\S+)', s)[0]
  if s.startswith('/lhcb'):  
    return utype, s

  ## Finally, pass-through with wraning
  logger.warning('Uncertain uri type, leave as PFN: '+s)
  return UriType.PFN, s


# def LHCbDataset__iadd__(self, other):
#   """DISABLED. Incorrect, need to merge the xml catalogue too."""
#   s1 = set(self.files)
#   s2 = set(other.files)
#   self.files = list(s1|s2)
#   return self


def _supported(fname):
  """
  Return True if given filename is supported for LHCbDataset re-extraction.

  >>> _supported('AllStream.dst')
  True
  >>> _supported('Gauss.XGEN')
  True
  >>> _supported('file.root')
  False
  """
  list_suffix = ( '.sim', '.gen', '.xgen', '.digi', '.xdigi', '.dst', '.ldst' )
  return any(fname.lower().endswith(suffix) for suffix in list_suffix)

# def _newfile(s):
  # return GPI.DiracFile(lfn=s) if s.startswith('LFN:') else GPI.LocalFile(s)

def LHCbDataset__getitem__(self, arg):
  """Patching for new LHCbDataset[] which broke XMLCatalogueSlice"""
  return GPI.LHCbDataset(files=self.files[arg], XMLCatalogueSlice=self.XMLCatalogueSlice)


def LHCbDataset_new(cls, *args, **kwargs):
  """
  Accept list of heterogeneous input, each one will face their parser.

  ## Part I: Homogenize the wide range of possible inputs
  
  - String  : Any uri of type PFN/LFN/BKQ are supports
  - Job     : The outputdata of given job will be extracted.
  - Iterable: (IO-open, glob, list-of-string)

  ## Part II: Seperation between different uritype

  - PFN: Ready, there's nothing to do 
  - LFN: Also ready, queuing for catalogue
  - BKQ: Need to call BKQuery and resolve into list of LFNs

  ## Part III: Prep&cache catalogue then assemble output dataset

  - Use LHCbDataset.getCatalogue to retrieve and cache xmlcatalogue
  - Report & skip missing if necessary (early-resolve before job 
    submission can help eliminate bad files. There was a scenario 
    where one file missing in the dataset and the entire job cannot 
    be submitted, reporting obsecure message...

  ## kwargs

  - catalog (bool): If False, do not attempt to resolve LFN with accessURL.
                    Can greatly help with the submission on non-Dirac node.
                    Default to True.
  - ignore_missing (bool)

  - force_reload (bool): This will punching through all functions inside that 
                         have caching enabled.
                         - get_catalog_lfn
                         - get_catalog_bkq
                         - get_raw_list_LFN

  """

  ### Part 0: Figure the optional keyword-arguments  
  kw_catalog        = kwargs.get('catalog'       , True )
  kw_ignore_missing = kwargs.get('ignore_missing', False)
  kw_force_reload   = kwargs.get('force_reload'  , False)  # TODO

  ### Part 1: Prepare raw atomic queue
  logger.debug(args)
  queue_raw, xml_entries = homogenize_inputs(*args)

  ### Part 2: Prep each utypes
  queue_files     = []   # These are entries ready for LHCbDataset()
  queue_lfn_nocat = []   # List of LFN with missing catalog, pending accessURL resolultion
  xml_entries     = []   # List of XML-entry to be concatenate.

  ### 2.1: 1st-pass: Breakdown composite type (BKQ,XML) to smaller ones.
  for uri in queue_raw:
    utype, uri = uri_identifier(uri)
    if utype is None:  # ignore...
      continue

    if utype.PFN:
      queue_files.append( uri )

    if utype.LFN:
      if kw_catalog:

        ## conflict between early_giveup, force_reload. Handle with care
        if kw_force_reload:
          res = get_catalog_lfn(uri, force_reload=True)
        else:
          res = get_catalog_lfn(uri, early_giveup=True)

        if res:
          queue_files.append( 'LFN:'+uri )
          xml_entries.append  ( res )
        else:
          queue_lfn_nocat.append( uri )
      else:
        queue_files.append( 'LFN:'+uri )  

    if utype.BKQ:
      lfns = get_raw_list_LFN(uri, force_reload=kw_force_reload)
      ## Call this only if `catalog` is requested
      if kw_catalog:
        ## Don't early_giveup as a whole. Attempt to look inside..
        res = get_catalog_bkq(uri, force_reload=kw_force_reload)  
        if res:
          ## So the entire catalog is ready. Good.
          queue_files.extend( 'LFN:'+lfn for lfn in lfns )
          xml_entries.append( res )
        else:
          ## Attempt each lfn in BKQ 1-by-1
          for lfn in lfns:
            ## If force_reload, well, force-reload
            # If not, then early_giveup by default, postpone for later.
            if kw_force_reload:
              res = get_catalog_lfn(lfn, force_reload=True)
            else:
              res = get_catalog_lfn(lfn, early_giveup=True)

            if res:
              queue_files.append( 'LFN:'+lfn )
              xml_entries.append( res )
            else:
              queue_lfn_nocat.append( lfn )
      else:
        queue_files.extend( 'LFN:'+lfn for lfn in lfns )


    if utype.XML:
      # abort if not exists
      if not os.path.exists(uri):
        logger.warning('XML non-existent, skip: '+uri)
        continue
      ## Use same engine as before, nice!
      with open(uri) as fin:
        rawdat = fin.read()
      rawdat = _rawxml_parser(rawdat)
      queue_files.extend  ( 'LFN:'+lfn for lfn in rawdat )
      xml_entries.extend( rawdat.values() )

  logger.debug('queue_files: %r'%queue_files)

  ### Part 3: Get catalogue, with manner
  ## If prefetching is needed, give a warning first...
  if queue_lfn_nocat and kw_catalog:
    ## If ignore, just notify how many files were ignored
    if kw_ignore_missing:
      logger.warning('Ignoring these [%i] file because of missing LFN->PFN link.'%len(queue_lfn_nocat))
      for lfn in queue_lfn_nocat:
        logger.warning(lfn)
    else:
      logger.debug('LFN missing catalog')
      for lfn in queue_lfn_nocat:
        logger.debug(lfn)
      res = raw_input(_msg_1stpass_warning%len(queue_lfn_nocat))
      # Fork the background caching
      if res == 'Y':
        _cache_catalog_lfns( queue_lfn_nocat )
      ## Abort anyhow.
      raise ValueError('LHCbDataset.new abort due to missing prefetch. Try me later...')


  ## Already okay, construct the resultant ds
  ds = cls(files=queue_files)  # Old style, become much slower in v601

  # from multiprocessing import Pool 
  # p = Pool(16)
  # ds = cls(p.map( _newfile, queue_files ))

  ## DISABLE FOR NEW v601 GANGA
  if kw_catalog and xml_entries:  ## Requested for catalog resolution & have entry 
    # if xml_entries:  # Has at least one entry to attach.
    ## if xml_entries OR missing_dump_file
    content = XMLTEMPLATE.format(''.join(sorted(list(set(xml_entries)))))
    xmlpath = dump_to_file(content)
    ds.XMLCatalogueSlice = xmlpath
  return ds

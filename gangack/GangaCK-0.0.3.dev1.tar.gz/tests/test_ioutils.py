#!/usr/bin/env py.test

import pytest

from GangaCK import IOUtils, GPI

#===================#
# BKQUERY OPERATION #
#===================#

def test_get_raw_list_LFN_null(monkeypatch):
  monkeypatch.setattr('GangaCK.IOUtils.parse_bkq_uri', lambda x: list())
  monkeypatch.setattr('GangaCK.OfflineGPI.LHCbDataset.files', None)
  
  with pytest.raises( ValueError ):
    print IOUtils.get_raw_list_LFN(None)
  assert IOUtils.get_raw_list_LFN.counter == (0,0) # Failed mid-call before reaching counter.

def test_get_raw_list_LFN_good(monkeypatch):
  res    = [ 'lfn1.dst', 'lfn2.dst', 'lfn3.dst' ]
  inputs = [ type('File', (), {'name':x})() for x in res ]

  monkeypatch.setattr('GangaCK.IOUtils.parse_bkq_uri', lambda x: list())
  monkeypatch.setattr('GangaCK.OfflineGPI.LHCbDataset.files', inputs)

  assert IOUtils.get_raw_list_LFN(None) == res
  assert IOUtils.get_raw_list_LFN.counter == (0,1) # Not persisted

#-------------------------------------------------------------------------------

## TODO: recover me
# def test_has_workers_running_false(monkeypatch):
#   res = [('Worker_0', 'idle', 'N/A'), ('Worker_1', 'idle', 'N/A')]
#   monkeypatch.setattr('GangaCK.OfflineGPI._ThreadPoolQueueMonitor.worker_status', lambda x: res)
#   # print GangaCK.OfflineGPI.queues._ThreadPoolQueueMonitor__user_threadpool.worker_status
#   assert IOUtils.has_workers_running() == False

## TODO: recover me
# def test_has_workers_running_false2(monkeypatch):
#   res = [('Worker_0', 'idle', 'N/A'), ('Worker_1', 'running', 'N/A')]
#   monkeypatch.setattr('GangaCK.OfflineGPI._ThreadPoolQueueMonitor.worker_status', lambda x: res)
#   assert IOUtils.has_workers_running() == True


#================#
# LFN OPERATIONS #
#================#

def test_lfn_put_return_None_on_failed(monkeypatch, testuser):
  metadata = {'Value': {'Successful': True, 'Failed': True}}
  monkeypatch.setattr( 'GangaCK.OfflineGPI.DiracFile.getMetadata', lambda x: metadata, raising=False)
  #
  res = IOUtils.lfn_put( '/local/path/to/file.root' )
  assert res == None

def test_is_LFN_uptodate(monkeypatch):
  ## Borrow the local file for checksum test
  checksum = '81925728'  # This is known in advance
  monkeypatch.setattr('GangaCK.IOUtils.lfn_checksum', lambda x: checksum)
  assert IOUtils.is_LFN_uptodate('tests/res/__postprocesslocations__', '/lfn/file.root')


#==================#
# Catalogue Cacher #
#==================#

lfn = '/lhcb/MC/2012/ALLSTREAMS.DST/00033128/0000/00033128_00000001_1.allstreams.dst'
entry = """<File ID="3EDD6971-3869-E311-821F-00266CF33118">
     <physical>
       <pfn filetype="ROOT_All" name="root://eoslhcb.cern.ch//eos/lhcb/grid/prod/lhcb/MC/2012/ALLSTREAMS.DST/00033128/0000/00033128_00000001_1.allstreams.dst" />
       <pfn filetype="ROOT_All" name="root://clhcbdlf.ads.rl.ac.uk//castor/ads.rl.ac.uk/prod/lhcb/MC/2012/ALLSTREAMS.DST/00033128/0000/00033128_00000001_1.allstreams.dst?svcClass=lhcbDst" />
       <pfn filetype="ROOT_All" name="root://ccdcacli067.in2p3.fr:1094/pnfs/in2p3.fr/data/lhcb/MC/2012/ALLSTREAMS.DST/00033128/0000/00033128_00000001_1.allstreams.dst" />
     </physical>
     <logical>
       <lfn name="/lhcb/MC/2012/ALLSTREAMS.DST/00033128/0000/00033128_00000001_1.allstreams.dst" />
     </logical>
   </File>"""

def test_rawxml_parser():
  with open('tests/res/catalog.xml') as fin:
    dat = fin.read()
  assert IOUtils._rawxml_parser(dat) == {lfn:entry}

def test_get_catalog_lfn(monkeypatch):
  with open('tests/res/catalog.xml') as fin:
    dat = fin.read()
  monkeypatch.setattr('GangaCK.OfflineGPI.LHCbDataset.getCatalog', lambda x: dat)
  assert IOUtils.get_catalog_lfn.func(lfn) == entry

#--------------

def test_get_catalog_bkq_good(monkeypatch):
  monkeypatch.setattr( 'GangaCK.IOUtils.get_raw_list_LFN' , lambda x: range(3) ) # Mock return of 3 lfn-uri
  monkeypatch.setattr( 'GangaCK.IOUtils.get_catalog_lfn'  , lambda x,early_giveup: 'XMLDATA%i\n'%x )
  assert IOUtils.get_catalog_bkq.func(None) == 'XMLDATA0\nXMLDATA1\nXMLDATA2\n'

def test_get_catalog_bkq_bad(monkeypatch):
  """If any of the `get_catalog_lfn` (with early_giveup) is None, it should abort."""
  monkeypatch.setattr( 'GangaCK.IOUtils.get_raw_list_LFN' , lambda x: range(3) ) # Mock return of 3 lfn-uri
  monkeypatch.setattr( 'GangaCK.IOUtils.get_catalog_lfn'  , lambda x,early_giveup: None if x==0 else 'XMLDATA\n' ) # contain None result
  assert IOUtils.get_catalog_bkq.func(None) == None

#--------------

def test_cache_catalog_lfns_ready(monkeypatch):
  monkeypatch.setattr( 'GangaCK.IOUtils.get_catalog_lfn', lambda x,early_giveup: 'XMLDATA' )
  assert IOUtils._cache_catalog_lfns(['lfn1', 'lfn2']) == None

def test_cache_catalog_lfns_waitqueue(monkeypatch):
  """If there's worker runnings, do not flush new queue yet."""
  monkeypatch.setattr( 'GangaCK.IOUtils.get_catalog_lfn', lambda x,early_giveup: None )
  monkeypatch.setattr( 'GangaCK.IOUtils.has_workers_running', lambda name: True )
  assert IOUtils._cache_catalog_lfns(['lfn1', 'lfn2']) == None

def test_cache_catalog_lfns_pooling(monkeypatch):
  monkeypatch.setattr( 'GangaCK.IOUtils.get_catalog_lfn', lambda x,early_giveup: None )
  monkeypatch.setattr( 'GangaCK.IOUtils.has_workers_running', lambda name: False )
  assert IOUtils._cache_catalog_lfns(['lfn1', 'lfn2']) == None

#=============#
# LHCbDataset #
#=============#

def test_homogenize_inputs_file(tmpdir):
  fname = 'hello.txt'
  dat   = "somefile.root"
  fpath = tmpdir.join(fname)
  fpath.write(dat)
  fin   = open(str(fpath))
  assert IOUtils.homogenize_inputs(fin)[0] == [dat]

def test_homogenize_inputs_lhcbdataset():
  files = ['123']
  ds    = GPI.LHCbDataset(files)
  assert IOUtils.homogenize_inputs(ds)[0] == files

def test_homogeneize_inputs_lhcbdataset_mergexml():
  ## xml-entries needs to be merged..., excluding duplicate if possibly
  ds1 = GPI.LHCbDataset(['1111'], XMLCatalogueSlice='tests/res/catalog.xml')
  ds2 = GPI.LHCbDataset(['2222'], XMLCatalogueSlice='tests/res/catalog.xml')
  files,entries = IOUtils.homogenize_inputs( ds1, ds2 )
  assert files   == [ '1111', '2222' ]
  assert entries == [ open('tests/res/catalog.txt').read() ] # inside data, header removed

def test_homogenize_inputs_flatten():
  ds  = GPI.LHCbDataset(['4'])
  res = IOUtils.homogenize_inputs( '1', ['2', '3'], ds)[0]
  assert res == [ '1' , '2', '3', '4' ]

#-------------------------------------------------------------------------------

def test_uri_identifier_pfn_local(tmpdir):
  ## For the file which deemed existed in file-system, return as PFN
  fin   = tmpdir.join('file.dst')
  fpath = str(fin)
  fin.write('CONTENT')
  assert IOUtils.uri_identifier(fpath) == ( IOUtils.UriType.PFN, 'PFN:'+fpath )

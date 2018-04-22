
import os
import pytest
from pprint import pprint

@pytest.fixture(autouse=True) # scope='session' fails
def add_namespace(doctest_namespace, monkeypatch):
  doctest_namespace['os'] = os
  doctest_namespace['pprint'] = pprint
  doctest_namespace['monkeypatch'] = monkeypatch

@pytest.fixture
def testuser(monkeypatch):
  """
  Fixture to monkeypatch user-sensitive setting to dummy one, suitable for doctest.
  """
  monkeypatch.delenv('GANGADIR', raising=False) # clean
  from GangaCK.OfflineGPI.config import Section
  # monkeypatch.setattr( Section, 'gangadir'        , '/home/testuser/gangadir' , raising=False)
  monkeypatch.setattr( Section, 'user'            , 'testuser'                , raising=False)
  monkeypatch.setattr( Section, 'DiracLFNBase'    , '/lhcb/user/t/testuser'   , raising=False)
  monkeypatch.setattr( Section, 'MassStorageFile' , {'uploadOptions':{'path':'/storage/testuser/'}}, raising=False)


# {'OK': True, 'Value': {'Successful': {'/lhcb/user/c/ckhurewa/PythonCK.zip': {'Status': 'AprioriGood', 'GID': 2703L, 'CreationDate': datetime.datetime(2015, 6, 2, 10, 28, 4), 'UID': 20296L, 'replicas': ['CERN-USER'], 'Checksum': 'fba3a47f', 'FileID': 184751753L, 'OwnerGroup': 'lhcb_user', 'ModificationDate': datetime.datetime(2015, 6, 2, 10, 28, 4), 'Size': 69942L, 'Mode': 509, 'Owner': 'ckhurewa', 'GUID': '8394EA63-6A2B-E6B4-5049-0E8C8E7826EA', 'ChecksumType': 'Adler32'}}, 'Failed': {}}}

@pytest.fixture(scope="function")
def dirac_success(testuser, monkeypatch):
  """Provide successful condition for DiracFile."""
  metadata = {'Value': {'Successful': {'/lhcb/user/t/testuser/somefile.root': {'Checksum': 'fba3a47f' }}, 'Failed': False}}
  monkeypatch.setattr( 'GangaCK.OfflineGPI.DiracFile.getMetadata', lambda x: metadata, raising=False)
  # request.addfinalizer(lambda: monkeypatch.undo())

# {'OK': True, 'Value': {'Successful': {}, 'Failed': {'/lhcb/user/c/ckhurewa/PythonCK.zi': 'No such file or directory'}}}

@pytest.fixture(scope="function")
def dirac_failed(testuser, monkeypatch):
  metadata = {'Value': {'Successful': {}, 'Failed': {'/lhcb/user/t/testuser/MISSING.root': 'No such file or directory'}}}
  monkeypatch.setattr( 'GangaCK.OfflineGPI.DiracFile.getMetadata', lambda x: metadata, raising=False)

@pytest.fixture
def res_gangarc(monkeypatch):
  """
  Set environmental variable for dummy gangarc file
  """
  monkeypatch.setenv('GANGA_CONFIG_FILE', 'tests/res/gangarc_test')

@pytest.fixture
def job197(monkeypatch):
  """
  Setup condition to ready job197 from test resource,
  used in many tests.

  """
  monkeypatch.setattr('GangaCK.ConfigUtils.dir_repository', lambda x=None: 'tests/res/r197' )
  monkeypatch.setattr('GangaCK.JobUtils.job_pfn_size'     , lambda x: 2048)
  monkeypatch.setattr('GangaCK.Jobtree.OfflineJobtreeReader.OfflineJobtreeReader.jobs_all', [197])  # For 197 in jobs_all check

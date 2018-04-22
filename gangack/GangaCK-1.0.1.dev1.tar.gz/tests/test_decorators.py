
import pytest
from GangaCK.Decorators import ijob_handler
# from GangaCK.JobUtils import OfflineJob

# import GangaCK
from GangaCK import GPI  # Patched

@pytest.fixture
def myfunc(tmpdir, testuser):
  @ijob_handler(basedir=tmpdir)
  def foo(intjid): 
    return intjid
  return foo

@pytest.fixture
def dummy_dat197(monkeypatch, testuser):
  monkeypatch.setattr('GangaCK.ConfigUtils.dir_repository', lambda x: 'tests/res/r197')

#-----------------------------------------

def test_incompat_signature(tmpdir):
  @ijob_handler(basedir=tmpdir)
  def badfoo(): pass
  with pytest.raises(TypeError):
    badfoo()

def test_invalid_jid(myfunc):
  ## Should raise due to bad jid given
  with pytest.raises(ValueError):
    myfunc(None)

def test_valid_jid(myfunc, dummy_dat197):
  assert myfunc(197)==197

def test_cache_increment(myfunc, dummy_dat197):
  # counter = (hit,total)
  assert myfunc.counter == (0,0)
  myfunc(197)
  assert myfunc.counter == (0,1)
  myfunc(197)
  assert myfunc.counter == (1,2)

def test_skipwrite(myfunc, dummy_dat197, monkeypatch):
  ## This should skip write (caching not activate) is status is ongoing
  monkeypatch.setattr(GPI.Job, 'is_final', False)
  assert myfunc.counter == (0,0)
  myfunc(197)
  assert myfunc.counter == (0,1)
  myfunc(197)
  assert myfunc.counter == (0,2)

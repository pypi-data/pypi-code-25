# FancyPipe
# ---------
# FancyPipe is a pure python package that takes care of those
# aspects of complex data processing pipelines that would otherwise 
# distract you from your main job: the design of the processing steps.
#
# FancyPipe takes care of
# * command line parsing
# * logging to dynamic html-file and console
# * parallel execution
# * temporary file management
# * error handling
# * reading parameters from a configuration file
# * running external commands
#
# To use FancyPipe effectively, you need to wrap your processing steps 
# as FancyTask classes, and define input-output connections between tasks.
#
# FancyPipe works in both Python 2.7 and Python 3
#
# Links used while developing this code:
# https://pythonhosted.org/joblib/parallel.html
# http://eli.thegreenplace.net/2012/01/24/distributed-computing-in-python-with-multiprocessing
# http://bugs.python.org/issue7503
# https://www.artima.com/weblogs/viewpost.jsp?thread=240845
#

from __future__ import print_function
from __future__ import unicode_literals

# These functions and classes get imported after "from fancypipe import *"
__all__ = [
  'assertPassword','assertBool','assertFile','assertOutputFile','assertDir','assertList','assertMultiSelect','assertDict','assertExec','assertToken',
  'assertMatch','assertInstance','assertType','assertSelect',
  'odict',
  'FANCYDEBUG','FancyReport',
  'FancyOutputFile','FancyTempFile','FancyPassword','FancyLog','FancyRequest','FancyValue','FancyArgs','FancyList','FancyDict',
  'FancyTask','FancyTaskInstance','FancyExec','FancyTaskManager',
  
]

import os,sys
import os.path as op
import argparse, subprocess
import tempfile, datetime, json
import codecs
from collections import OrderedDict
import inspect
import re,uuid
import threading, multiprocessing, multiprocessing.queues, multiprocessing.managers
try:
  import queue
except ImportError:
  import Queue as queue
try:
  import cPickle as pickle
except ImportError:
  import pickle
import traceback
import string,StringIO, random
import gc # garbage collection

# Global task manager and worker thread/process
global_taskManager = None

# Constants to indicate what type of result a task returns.
Result_Success = 0
Result_Failed = 1
Result_Print = 2
Result_Log = 3

# Constants to indicate what to log.
Log_Task = 1
Log_Input = 2
Log_Output = 4

## Constants to indicate the run-status of a task.
Task_Reset = 0
Task_ResolvingInput = 1
Task_Submitted = 2
Task_ResolvingOutput = 3
Task_Completed = 4
Task_Failed = 5

# Print a message from a possibly remote worker.
# DEPRECATED: use FancyTask self.print
#def fancyPrint(s):
#  global_taskManager.print(s)

# Create log file entry from a possibly remote worker.
# DEPRECATED: use FancyTask self.log
#def fancyLog(msg,errorLevel):
#  global_taskManager.logFile(global_taskManager.runningTask,data,name,tp)

# Create log file entry from a possibly remote worker.
def fancyConsole(msg,errorLevel=0):
  global_taskManager.logConsole(global_taskManager.runningTask,msg,errorLevel)

# Ordered dictionary class for setting inputs/outputs.
class odict(OrderedDict):
  def __init__(self, *keyvals):
    try:
      OrderedDict.__init__(self,*keyvals)
    except:
      OrderedDict.__init__(self)
      if keyvals and keyvals[0]:    
        if isinstance(keyvals[0],(tuple,list)):
          OrderedDict.__init__(self,keyvals)
        else:
          for i in range(0,len(keyvals),2):
            self[keyvals[i]] = keyvals[i+1]

  def extend(self,keyvals,*keys):
    for k in keys:
      self[k] = keyvals[k]
#endclass

# Password class that hides the password in logs
class FancyPassword:
  def __init__(self,pwd):
    self.value = pwd
  def __repr__(self):
    return '***'

# Assert functions are used to parse and validate command line inputs
def assertPassword(s):
  return FancyPassword(s)

def assertBool(s):
  if (s is True or s.lower() == 'true' or s == '1'): return True
  elif (s is False or s.lower() == 'false' or s == '0'): ans = False
  else: raise AssertionError('Option "{}" does not represent a boolean value.'.format(s))

def assertFile(s):
  """ Assert that the input is an existing file. """
  if not op.isfile(s): raise AssertionError('String "{}" is not an existing file.'.format(s))
  return s

def assertOutputFile(s):
  """ Assert that the input is a valid filename, to be used as an output file. """
  if not os.access(op.dirname(s), os.W_OK): raise AssertionError('String "{}" does not represent a valid output file.'.format(s))
  return FancyOutputFile(s)

def assertDir(s):
  """ Assert that the input is an existing directory. """
  if not op.isdir(s): raise AssertionError('String "{}" is not an existing directory.'.format(s))
  return s

def assertList(s):
  """ Assert that the input is a list or tuple. """
  if isinstance(s,str):
    try:
      s = json.loads(s)
    except ValueError:
      try:
        with open(s) as fp:
          s = json.load(fp)
      except:
        raise
    except:
      raise
  if not isinstance(s,(list,tuple)): raise AssertionError('Variable "{}" is not a list.'.format(s))
  return s

def assertMultiSelect(s):
  """ Assert that the input selects one or multiple pages, like 1,2,4-8 """
  if isinstance(s,str):
    parts = s.lstrip('[').rstrip(']').split(',')
    s = []
    for p in parts:
      p = [int(v) for v in p.split('-')]
      if len(p)>1: p = range(p[0],p[1]+1)
      s.extend(p)
    s = list(set(s))
  return assertList(s)
  
def assertDict(s):
  """ Assert that the input is a dictionary. """
  if isinstance(s,str): 
    try:
      s = json.loads(s)
    except ValueError:
      try:
        with open(s) as fp:
          s = json.load(fp)
      except:
        raise
    except:
      raise
  # convert list to dictionary if necessary
  if isinstance(s,(list,tuple)): s = { i:v for i,v in enumerate(s) }
  if not isinstance(s,dict): raise AssertionError('Variable "{}" is not a dictionary.'.format(s))
  return s

def assertExec(s):
  """ Assert that the input can be executed and return the full path to the executable. """
  import os
  def is_exe(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

  fpath,fname = op.split(s)
  if fpath:
    if is_exe(s):
      return s
  else:
    for path in os.environ["PATH"].split(os.pathsep):
      path = path.strip('"')
      exe_file = op.join(path,s)
      if is_exe(exe_file):
        return exe_file
  raise AssertionError('Cannot find executable command "{}".'.format(s))

def assertToken(s):
  return s.strip()

# call as assertMatch(...)
def assertMatch(regexp,fromStart=True,decompose=True):
  def f(s):
    if fromStart: matches = re.match(regexp,s)
    else: matches = re.search(regexp,s)
    if matches: 
      if decompose: return matches.groups()
      else: return s
    raise AssertionError('String "{}" has no match for regular expression "{}".'.format(s,regexp))
  return f

# call as assertInstance(...)
def assertInstance(cls):
  def f(v):
    if isinstance(v,cls): return v
    raise AssertionError('Variable "{}" is not an instance of "{}".'.format(v,cls))
  return f

# call as assertType(...)
def assertType(tp,allow=set()):
  def f(v):
    try: 
      return tp(v)
    except ValueError:
      if v in allow:
        return allow[v]
      else:
        raise AssertionError('Value "{}" cannot be converted to type "{}".'.format(v,tp))
  return f

# call as assertSelect(...)
def assertSelect(*choices):
  def f(s):
    if s in choices:
      return s
    else:
      raise AssertionError('Value "{}" isn\'t one of: {}.'.format(s,choices))
  return f

def assertJobServer(v):
  if v:
    addr = v.split(':')
    port = int(addr[1]) if len(addr)>1 else 51423
    return (addr[0],port)
  else:
    return v
    
## Use for debugging: prints argument values and their context in contrasting green
def FANCYDEBUG(*args,**kwargs):
  traceback = kwargs['traceback'] if 'traceback' in kwargs else 3
  frame = inspect.currentframe()
  outerframes = inspect.getouterframes(frame)
  msg = '___\n'
  try:
    msg += ''.join(['{}. {}\n'.format(i,v[4][0].strip()) for i,v in enumerate(outerframes[1:min(len(outerframes),traceback+1)])])
  except:
    pass
  msg += '\n'.join([repr(FancyReport.jsonifyValue(v,summarize=True)) for v in args])+'\n'
  FancyReport.warning(msg)


## Use this class to indicate that the string represents an outputfile.
## In resume mode, fancypipe will check whether the file can be reused.
class FancyOutputFile(str):
  pass
#endclass


## Use this class to indicate that the string represents a temporary file.
## It will be removed when no longer needed.
class FancyTempFile(FancyOutputFile):
  pass
#endclass


class ArgParse:
  # Parse external inputs, from commandline or configfile.
  @staticmethod
  def _parseInputs(inputs,raw,cfg,presets={}):
    if inputs is None: return {}
    kwargs = {}
    errors = []
    for key,inp in inputs.items():
      dest = key.replace('-','_');
      if key in presets:
        kwargs[dest] = presets[key]
      elif key in cfg:
        # typecast
        tp = inp['type'] if 'type' in inp else str
        kwargs[dest] = tp(cfg[key])
      elif 'default' in inp:
        if hasattr(inp['default'],'__call__'):
          kwargs[dest] = inp['default'](kwargs)
        else:
          kwargs[dest] = inp['default']
    if raw is not None:
      for key,inp in inputs.items():
        dest = key.replace('-','_');
        if dest in raw:
          # typecast
          tp = inp['type'] if 'type' in inp else str
          kwargs[dest] = tp(raw.pop(dest))
        elif dest not in kwargs:
          errors.append('Missing input "{}". Searched commandline arguments, configuration file and default.'.format(key))
    if errors: raise ValueError('\n'.join(errors))
    return kwargs

  @staticmethod
  def parseInputs(cls,cmdArgs,fancyConfig=None,presets={}):
    configArgs = fancyConfig.classDefaults(cls.__name__) if fancyConfig else {}
    return ArgParse._parseInputs(cls.inputs,cmdArgs,configArgs,presets)
#endclass


## Used for output and error reporting, with an option to use json-rpc 2
class FancyReport:
  inputs = odict(
    ('jsonrpc2',dict( action='store_true', default=False,
      help='Capture output and return result in jsonrpc2 format.')
    )
  )
    
  rpc_id = None
  
  def __init__(self,jsonrpc2=False):
    if jsonrpc2:
      # capture output from print statements
      self.stdout0 = sys.stdout
      self.stdout1 = StringIO.StringIO()
      sys.stdout = self.stdout1 # redirect
      self.stderr0 = sys.stderr
      self.stderr1 = StringIO.StringIO()
      sys.stderr = self.stderr1 # redirect
      self.rpc_id = str(uuid.uuid4())
      
  def uncapture(self):
    sys.stdout = self.stdout0
    sys.stderr = self.stderr0
    return self.stdout1.getvalue()

  def __del__(self):
    if self.rpc_id:
      self.uncapture()
      self.rpc_id = None

  @staticmethod
  def warning(s): sys.stderr.write('\033[1;32m{}\033[0m\n'.format(s))
  
  @staticmethod
  def error(s): sys.stderr.write('\033[1;31m{}\033[0m\n'.format(s))

  @staticmethod
  def traceback():
    exc_type, exc_value, exc_traceback = sys.exc_info() 
    return traceback.format_exception(exc_type, exc_value, exc_traceback)

  @staticmethod
  def errorTrace(e=None):
    args = {}
    if (e):
      for k in dir(e):
        if k[0] != '_':
          args[k] = getattr(e,k)
    exc_type, exc_value, exc_traceback = sys.exc_info() 
    tb = traceback.format_exception(exc_type, exc_value, exc_traceback)
    msg = tb.pop()
    return dict(args=args,exception=exc_type.__name__,message=msg,traceback=tb)
    
  def success(self,result):
    if self.rpc_id:
      self.uncapture()
      result = {
        'jsonrpc':'2.0',
        'id':self.rpc_id,
        'result': FancyReport.jsonifyValue(result),
        'stdout': self.stdout1.getvalue(),
        'stderr': self.stderr1.getvalue()
      }
      indent = 2
    else:
      result = FancyReport.jsonifyValue(result,summarize=True)
      indent = 2
    print(json.dumps(result,indent=indent))

  def fail(self,msg,code=1):
    traceback = self.traceback()
    msg = traceback.pop()
    if self.rpc_id:
      self.uncapture()
      result = {
        'jsonrpc':'2.0',
        'id': self.rpc_id,
        'error':{
          'code': code,
          'message': msg,
          'data': {
            'stdout': self.stdout1.getvalue(),
            'stderr': self.stderr1.getvalue(),
            'traceback': traceback
          }
        }
      }
      print(json.dumps(result,indent=2))
      sys.exit(0)
    else:
      result = '{}\n{}\n\n'.format(msg,''.join(FancyReport.traceback()))
      FancyReport.error(result)
      sys.exit(code)

  @staticmethod
  def jsonifyValue(v,summarize=False):
    if not summarize and hasattr(v,'tolist'): return v.tolist()
    if isinstance(v,(tuple, list)): return FancyReport.jsonifyList(v,summarize)
    if isinstance(v,(dict)): return FancyReport.jsonifyDict(v,summarize)
    if isinstance(v,(int,bool,float)) or v is None: return v
    if hasattr(v,'jsonify'): return v.jsonify(summarize)
    return v if isinstance(v,(str,unicode)) else str(v)

  @staticmethod
  def jsonifyList(args,summarize=False):
    n = len(args)
    if summarize and n>32:
      args = [ args[i] for i in [0,1,2,3,-2,-1,0] ]
      args[3] = '... array({}) ...'.format(n-6)
    return [FancyReport.jsonifyValue(v,summarize) for v in args]

  @staticmethod
  def jsonifyDict(kwargs,summarize=False):
    items = kwargs.items()
    if summarize and len(items)>32:
      items = [ items[i] for i in [0,1,2,3,-2,-1,0] ]
      items[3] = ('(...)','(...)')
    return { str(k):FancyReport.jsonifyValue(v,summarize) for k,v in items }
#endclass


## Used for logging to console and html-file.
class FancyLog:
  def __init__(self, logDir=None, tryResume=False):
    self.logDir = logDir
    self.logFile = None
    if logDir:
      if not op.isdir(logDir):
        print('Creating new log directory "{}".'.format(logDir))
        os.makedirs(logDir)
      logFilesDir = op.join(logDir,'fancylog_files')
      if not op.isdir(logFilesDir):
        os.mkdir(logFilesDir)
      self.logDir = logDir
      self.logFile = op.join(logDir,'fancylog.js')
      if op.isfile(self.logFile) and tryResume:
        self.resumeLog()
      else:
        self.initLog()
  
  def initLog(self):
    with codecs.open(self.logFile,'w',encoding='utf-8') as log:
      log.write('var LOG = [];\n\n')
    htmlSrc = op.join(op.dirname(__file__),'fancylog.html')
    htmlDest = op.join(self.logDir,'fancylog.html')
    if not op.isfile(htmlSrc):
      import shutil
      shutil.copyfile(htmlSrc,htmlDest)

  def resumeLog(self):
    pass
    
  def appendLog(self,logItem):
    if not self.logDir: return
    with codecs.open(self.logFile,'a',encoding='utf-8') as log:
      log.write('LOG.push('+json.dumps(logItem)+')\n')

  @staticmethod
  def logTask(task):
    starttime = datetime.datetime.now()
    cmd = task.getName()
    title = task.title
    item = dict(
      id = str(task),
      cmd = cmd,
      timeStamp = starttime.isoformat(),
    )
    if task.logLevel & Log_Input:
      if task.myInput.args: item['args'] = FancyReport.jsonifyList(task.myInput.args,summarize=True)
      if task.myInput.kwargs: item['kwargs'] = FancyReport.jsonifyDict(task.myInput.kwargs,summarize=True)    
      return LogItem(**item)
    
  @staticmethod
  def logMessage(task,name,msg,tp='message'):
    starttime = datetime.datetime.now()
    if not isinstance(msg,str):
      msg = FancyReport.jsonifyValue(msg,summarize=True)
    return LogItem(
      attachTo = str(task), 
      name = name,
      data = msg,
      type = tp,
      timeStamp = starttime.isoformat()
    )

  @staticmethod
  def printMessage(task,msg,name=None):
    return (
      '__{}__\n{}'.format(name,msg) if name else msg,
      str(task),
      '1;36'
    )

  @staticmethod
  def logError(task,errorTrace):
    return FancyLog.logMessage(task,errorTrace['message'],errorTrace['traceback'],tp='error')

  @staticmethod
  def printError(task,errorTrace):
    return (
      '{}\n{}'.format(errorTrace['message'],errorTrace['traceback']),
      str(task),
      '1;31'
    )

  @staticmethod
  def logResult(task,name,data):
    return FancyLog.logMessage(task,name,data,tp='result')

#endclass


## Used by FancyLog to contain item that can be written to logfile 
class LogItem(dict):
  def __init__(self,**kwargs):
    dict.__init__(self,kwargs)
#endclass


## Used to keep track of temporary (result) files.
class FancyClean:
  def __init__(self):
    self.files = set()
    self.dirs = set()

  def update(self,files,dirs=None):
    self.files.update(files)
    if dirs: self.dirs.update(dirs)
  
  def addNewFile(self,f,doCleanup):
    if doCleanup and not op.isfile(f): self.files.add(f)
        
  def addCreateDir(self,d,doCleanup):
    create = []
    while not op.exists(d):
      create.append(d)
      head,tail = op.split(d)
      d = head
    for d in reversed(create):
      try:
        os.mkdir(d)
        if doCleanup: self.dirs.add(d)
      except OSError: # thrown if two processes try to create dir at the same time
        pass

  def cleanup(self,exclude,taskId):
    if (not self.files and not self.dirs): return (set(),set())
    excludedFiles = set()
    excludedDirs = set()
    E = set()
    for path in exclude:
      E.add(op.realpath(path))
    for f in self.files:
      F = op.realpath(f)
      if F not in E:
        try:
          os.remove(f)
          print('{} deleted file "{}".'.format(taskId,f))
        except:
          FancyReport.warning('{} tried to delete file "{}", but failed.'.format(taskId,f))
      else:
        excludedFiles.add(f)
    for d in reversed(sorted(self.dirs)):
      D = op.realpath(d)
      try:
        os.rmdir(d)
        print('{} removed folder "{}".'.format(taskId,d))
      except:
        excludedDirs.add(d)
    return (excludedFiles,excludedDirs)
#endclass


## Used to load and keep track of configuration parameters.
class FancyConfig:
  inputs = odict(
    'configFile', dict(
      type=assertFile, default=None,
      help='Configuration file (XML or JSON) to read default parameters from. Default: None.'
    )
  )
  
  def __init__(self,config={}):
    self.config = config

  @staticmethod
  def etree_to_odict(t):
    if len(t):
      od = odict()
      for ch in t:
        od[ch.tag] = FancyConfig.etree_to_odict(ch)
      return od
    else:
      return t.text

  @classmethod
  def fromFile(cls,configFile):
    if configFile is None:
      return cls()
    name,ext = op.splitext(configFile)
    if ext.lower() == '.xml':
      from lxml import etree
      tree = etree.parse(configFile)
      root = tree.getroot()
      config = FancyConfig.etree_to_odict(root)
      if root.tag != 'config': config = odict((root.tag,config))
      return cls(config)
    elif ext.lower() == '.json':
      return cls(json.load(configFile, object_pairs_hook=odict))
    else:
      raise RuntimeError('Configuration file "{}" has an unrecognized format.'.format(configFile))

  @classmethod
  def fromParent(cls,parentTask):
    try:
      config = parentTask.fancyConfig.config.copy()
      parentClass = parentTask.__class__.__name__
      if parentClass in config:
        # overwrite defaults with className-specific defaults
        for k,v in config[parentClass].items(): config[k] = v;
        config.pop(parentClass)
      return cls(config)
    except:
      return cls()
    
  def classDefaults(self,taskClass):
    return self.config[taskClass] if taskClass in self.config else {}
#endclass


## Contains a request for output <outKey> of task <task>.
class FancyRequest:
  def __init__(self,task,outKey):
    self.task = task # task that will supply the value
    self.outKey = outKey # key of the above task's output (or ALL for complete output)
      
  def __getitem__(self,key):
    return FancyRequestItem().updateInput(self,key).requestOutput()
    
  def __repr__(self):
    return 'FancyRequest<{}[{}]>'.format(self.task,self.outKey)
#endclass
  
  
## Class that represents ALL arguments
class ALL:
  def __repr__(self):
    return 'ALL'
#endclass


## Base class for task input/output, with a single argument
class FancyValue:
  def __init__(self,value):
    self.value = value
  
  def getValue(self): 
    return self.value
  
  def jsonify(self,summarize=False):
    return FancyReport.jsonifyValue(self.getValue(),summarize)
    
  def __repr__(self):
    return repr(self.jsonify())

  def __str__(self):
    return str(self.jsonify(summarize=True))

  @staticmethod
  def _ready(v):
    return False if isinstance(v,FancyRequest) else v.ready() if isinstance(v,FancyValue) else True

  def ready(self):
    return self._ready(self.value)

  @staticmethod
  def _tempfiles(ans,v):
    if isinstance(v,FancyTempFile): ans.add(str(v))
    elif isinstance(v,FancyValue): ans.update( v.tempfiles() )

  def tempfiles(self):
    ans = set()
    self._tempfiles(ans,self.value)
    return ans

  def __getitem__(self,key):
    if key is ALL: return self.value
    else: return self.value[key]

  def __setitem__(self,key,val):
    if key is ALL: self.value = val
    else: self.value[key] = val

  def resolve(self):
    if not global_taskManager.runningTask:
      raise RuntimeError('FancyValue.resolve() must be called from within the main() method of a FancyTask.')
    pendingTasks = global_taskManager.runningTask.initRequests(self)
    if pendingTasks: global_taskManager.resolve( pendingTasks )
#endclass


## FancyValue with only positional arguments.
class FancyList(list,FancyValue):
  def __init__(self,*args):
    if len(args)>1:
      raise TypeError('FancyList takes only one argument (a list or tuple).')
    args = args[0] if len(args)>0 else []
    if not isinstance(args,(list,tuple)):
      raise TypeError('FancyList argument must be a list or tuple.')
    list.__init__(self,args)
    self.args = self

  def getValue(self): 
    return self
  
  def ready(self):
    for i,v in enumerate(self):
      if not self._ready(v): return False
    return True

  def tempfiles(self):
    ans = set()
    for i,v in enumerate(self):
      self._tempfiles(ans,v)
    return ans
#endclass


## FancyValue with only keyword arguments.
class FancyDict(dict,FancyValue):
  def __init__(self,*args,**kwargs):
    if not kwargs:
      if len(args)>1:
        raise TypeError('FancyDict takes only one positional argument (a dict).')
      kwargs = args[0] if len(args)>0 else {}
    dict.__init__(self,kwargs)
    self.kwargs = self

  def getValue(self):
    return self
  
  def ready(self):
    for k,v in self.items():
      if not self._ready(v): return False
    return True

  def tempfiles(self):
    ans = set()
    for k,v in self.items():
      self._tempfiles(ans,v)
    return ans
#endclass


## FancyValue with positional and keyword arguments
class FancyArgs(FancyValue):
  def __init__(self,*args,**kwargs):
    self.args = FancyList(args)
    self.kwargs = FancyDict(kwargs)

  def getValue(self): 
    return dict(args=self.args,kwargs=self.kwargs)
  
  def ready(self):
    return self.args.ready() and self.kwargs.ready()

  def tempfiles(self):
    return self.args.tempfiles() | self.kwargs.tempfiles()

  def __getitem__(self,key):
    return self.args[key] if isinstance(key,int) else self.kwargs[key]

  def __setitem__(self,key,val):
    if isinstance(key,(int)): self.args[key] = val
    else: self.kwargs[key] = val
    
  def items(self): 
    return self.kwargs.items()
#endclass


## Fancy task class, supports parallel execution, logging, tempdir, config file.
class FancyTask:
  """ Task--specific settings """
  # short name to identify task (None to use class name)
  name = None
  # task title used for logging
  title = None
  # task description used for documentation
  description = None
  # if defined, then main() must have matching inputs
  inputs = None
  # if defined, then main() must have matching outputs
  outputs = None
  # run job in parallel, if possible
  runParallel = False
  # abort the pipeline when this task fails
  abortOnError = True
  # run main every time that part of the input becomes ready
  alwaysRunMain = False
  
  """ Settings normally inherited from parent Task or FancyTaskManager """
  # logLevel (None for inherit, 0 for no logging at all) 
  logLevel = None
  # verbosity (None for inherit, 0 for no console printing at all) 
  verbosity = None
  # cleanup temporary files when they are not referenced by any output (None for inherit)
  doCleanup = None
  # resume execution by trying to reuse existing temporary files (None for inherit)
  tryResume = None
  # FancyConfig object with parameters read from a configuration file
  fancyConfig = None

  """ Internal properties """
  _tempdir = None
  _numChildren = 0
  taskId = None
  parentId = None
  fancyClean = None
  requests = {}
  sourceLinks = {}
  
  def __init__(self,*args,**kwargs):
    if not global_taskManager:
       self = self.getStarted()
       
    parent = global_taskManager.runningTask
    if parent:
      # inherit from parent
      self._tempdir = op.join(parent._tempdir,self.tempsubdir(parent._numChildren))
      if self.taskId is None: self.taskId = parent.newChildId()
      if self.verbosity is None: self.verbosity = parent.verbosity # inherit
      if self.logLevel is None: self.logLevel = parent.logLevel # inherit
      if self.fancyConfig is None and parent.fancyConfig: self.fancyConfig = FancyConfig.fromParent(parent)
      if self.doCleanup is None: self.doCleanup = parent.doCleanup
      if self.tryResume is None: self.tryResume = parent.tryResume
      self.parentId = str(parent)
    elif isinstance(global_taskManager, FancyTaskManager):
      # inherit from task manager
      self._tempdir = global_taskManager.workDir
      self.taskId = global_taskManager.jobId
      self.logLevel = global_taskManager.logLevel
      self.verbosity = global_taskManager.verbosity
      self.fancyConfig = global_taskManager.fancyConfig
      self.doCleanup =  global_taskManager.doCleanup
      self.tryResume =  global_taskManager.tryResume
      self.parentId = str(self)
    else:
      raise RuntimeError("Global task manager found, but it is not a FancyTaskManager.") 

    self.setInput(*args,**kwargs)

  @classmethod
  def getStarted(cls,presets={},cmdArgs={},unusedArgs=None):
    # Get jsonrpc2 as early as possible, to capture errors
    parsedArgs = ArgParse.parseInputs(FancyReport,cmdArgs,presets=presets)
    jsonrpc2 = parsedArgs['jsonrpc2']
    report = FancyReport(jsonrpc2)

    try:
      if unusedArgs: report.warning('Unused arguments passed to class {}: {}'.format(cls,','.join(unusedArgs)))

      # Prepare fancyConfig
      parsedArgs = ArgParse.parseInputs(FancyConfig,cmdArgs,presets=presets)
      configFile = parsedArgs['configFile']
      fancyConfig = FancyConfig.fromFile(configFile)
  
      # Parse inputs
      parsedArgs = ArgParse.parseInputs(FancyTaskManager,cmdArgs,fancyConfig=fancyConfig,presets=presets)
      
      # TaskManager setup
      try: numWorkers = int(parsedArgs['numWorkers'])
      except: numWorkers = multiprocessing.cpu_count()
      # - this automatically sets global_taskManager
      FancyTaskManager(
        fancyReport = report,
        workDir = parsedArgs['workDir'] or op.join(tempfile.gettempdir(),cls.tempsubdir(0)),
        logDir = parsedArgs['logDir'],
        logLevel = parsedArgs['logLevel'],
        verbosity = parsedArgs['verbosity'],
        jobServer = parsedArgs['jobServer'],
        jobAuth = parsedArgs['jobAuth'],
        numWorkers = numWorkers,
        workerType = parsedArgs['workerType'][0],
        doCleanup = parsedArgs['doCleanup'],
        tryResume = parsedArgs['tryResume']
      ) 

      # Parse task inputs
      parsedArgs = ArgParse.parseInputs(cls,cmdArgs,fancyConfig=fancyConfig,presets=presets)
      
      # Instantiate
      self = cls(**parsedArgs)
    except:
      traceback = report.traceback()
      report.fail(msg='Fatal error in class {}.'.format(cls),)
        
    return self  
    
  @classmethod
  def fromCommandLine(cls,**presets):
    # Parse command line
    parser = FancyTaskManager._getParser(cls)
    (cmdArgs,unusedArgs) = parser.parse_known_args()
    cmdArgs = vars(cmdArgs)
    return cls.getStarted(presets,cmdArgs,unusedArgs)
        
  def __getitem__(self,keys):
    return self.requestOutput(*keys)

  def newChildId(self):
    self._numChildren += 1
    return self.taskId+'.'+str(self._numChildren)

  def getName(self):
    return self.name if self.name else self.__class__.__name__

  def __repr__(self):
    return '{}[{}]'.format(self.getName(), self.taskId)


  @classmethod
  def tempsubdir(cls,taskId):
    return '{}_{}'.format(taskId,cls.__name__)

  # tempdir(subdir) returns tempdir/subdir, and registers it for cleanup after running main()
  def tempdir(self,subdir=None,doCleanup=None):
    if self._tempdir is None:
      raise RuntimeError('You can only call tempdir() from within a task.')
    d = self._tempdir
    if subdir: 
      d = op.join(d,subdir)
    doCleanup = doCleanup if doCleanup is not None else self.doCleanup
    if not self.fancyClean:
      self.fancyClean = FancyClean()
    self.fancyClean.addCreateDir(d,doCleanup)
    return d

  # tempfile(f) returns tempdir/f, and registers it for cleanup after running main()
  def tempfile(self,f=None,ext='',doCleanup=None):
    if f is None:
      rand8 = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(8))      
      f = '{}_{}{}'.format(self.__class__.__name__.lower(),rand8,ext)
    f = op.join(self.tempdir(),f)
    doCleanup = doCleanup if doCleanup is not None else self.doCleanup
    if not self.fancyClean:
      self.fancyClean = FancyClean()
    self.fancyClean.addNewFile(f,doCleanup)
    return FancyTempFile(f)
  
  def getCommandLine(self):
    #return 'python runtask.py {} [...]'.format(self.__class__.__name__)
    return None

  # Get an input.
  def getInput(self,key=ALL):
    return self.myInput if key is ALL else self.myInput[key]

  # Set the input.
  def setInput(self,*args,**kwargs):
    self.runStatus = Task_Reset
    self.myInput = FancyArgs(*args,**kwargs)
    self.myOutput = None
    self.requests = {} # for each sourceKey, a list of target task ids to send the result to
    self.sourceLinks = {} # for each (sourceTask,sourceKey) a list of (targetArgs,targetKey) pairs that this task receives data from
    return self
    
  # Make task callable, returns task instance with inputs set.
  __call__ = setInput
    
  # Generate output requests, use these requests only 
  # to return as output of a task, or to set as input to another task.
  def _requestOutput(self,*keys):
    if keys:
      output = FancyList()
      for k in keys:
        output.append(FancyRequest(self,k))
    else:
      output = FancyRequest(self,ALL)
    return output

  def requestOutput(self,*keys):
    output = self._requestOutput(*keys)
    return output[0] if len(keys) == 1 else output
  
  # Called before getting any output.
  def finalizeInput(self):
    # Retrieve unset inputs from configuration file or defaults
    if self.inputs:
      configArgs = self.fancyConfig.classDefaults(self.__class__.__name__) if self.fancyConfig else {}
      myInput = self.myInput.kwargs
      for key,inp in self.inputs.items():
        dest = key.replace('-','_');
        if not dest in myInput:
          if key in configArgs:
            myInput[dest] = configArgs[key]
          elif 'default' in inp:
            if hasattr(inp['default'],'__call__'):
              myInput[dest] = inp['default'](myInput)
            else:
              myInput[dest] = inp['default']
          else:
            raise RuntimeError('No default value found for input "{}" of task {}.'.format(key,self))
    
  # Get one or more outputs, run task if necessary.
  def getOutput(self,*keys):
    output = self._requestOutput(*keys)
    if not isinstance(output,FancyValue): output = FancyValue(output)
    pendingTasks = global_taskManager.runningTask.initRequests(output)
    if pendingTasks: global_taskManager.resolve( pendingTasks )
    return output[0] if len(keys) == 1 else output.getValue()

  # Returns the name of the output file associated with output [key].
  def outputFile(self,key):
    if key in self.myInput:
      f = self.myInput[key]
      if isinstance(f,FancyOutputFile): return f
      
  # Recursively initialize output requests and return pending tasks.
  def initRequests(self,myArgs):
    
    def addRequest(inKey,req): # target key, task request
      task,outKey = (req.task,req.outKey)

      # Try to use previous result.
      if outKey is ALL:
        if task.runStatus is Task_Completed:
          myArgs[inKey] = task.myOutput.getValue()
          return False
      else:
        try:
          # Use previous result.
          myArgs[inKey] = task.myOutput[outKey]
          return False
        except (KeyError,TypeError):
          # No previous result.
          if task.runStatus is Task_Completed:
            # Perhaps the previous run did not return all possible outputs, rerun.
            FancyReport.warning('Task "{}" has status completed, but requested key "{}" was not found. Will try and run the task again.'.format(task,outKey))
            task.runStatus = Task_Reset
          elif task.tryResume:
            # Check for files that can be reused
            f = task.outputFile(outKey)
            if f and op.isfile(f):
              self.print('Recycling output file {} of task {}'.format(f,task))
              myArgs[inKey] = f
              return False

      if self.verbosity & Log_Task:
        self.print( *FancyLog.printMessage(self,'Requesting output "{}" from {}'.format(outKey,task)) )
      if not outKey in task.requests: task.requests[outKey] = set()
      task.requests[outKey].add(str(self))
      linkKey = (str(task),outKey)
      if not linkKey in self.sourceLinks: self.sourceLinks[linkKey] = []
      self.sourceLinks[linkKey].append((myArgs,inKey))
      return True

    pendingTasks = odict()
    mySources = odict()
    if isinstance(myArgs,FancyValue):
      if hasattr(myArgs,'args'):
        for i,v in enumerate(myArgs.args):
          if isinstance(v,FancyRequest):
            if addRequest(i,v): mySources[v.task] = 1
          elif isinstance(v,FancyValue):
            pendingTasks.update( self.initRequests(v) )
      if hasattr(myArgs,'kwargs'):
        for k,v in myArgs.kwargs.items():
          if isinstance(v,FancyRequest):
            if addRequest(k,v): mySources[v.task] = 1
          elif isinstance(v,FancyValue):
            pendingTasks.update( self.initRequests(v) )
      if hasattr(myArgs,'value'):
        v = myArgs.value
        if isinstance(v,FancyRequest):
          if addRequest(ALL,v): mySources[v.task] = 1

    for src in mySources.keys():
      if src.runStatus == Task_Reset:
        src.runStatus = Task_ResolvingInput
        pendingTasks.update( { str(src):src } )
        pendingTasks.update( src.initRequests(src.myInput) )

    return pendingTasks


  # Fulfill requests after running (some of) the pending tasks.
  def _fulfillRequests(self,taskCache):
    affectedTasks = odict()
    for outKey,targets in self.requests.items():
      linkKey = (str(self),outKey)
      try:
        val = None if self.runStatus is Task_Failed else self.myOutput.getValue() if outKey is ALL else self.myOutput[outKey]
      except KeyError: 
        raise KeyError('Task "{}" does not have the requested output "{}"'.format(self,outKey))
      for tgtKey in targets:
        if tgtKey == str(self):
          # special case when calling self.resolve()
          tgt = self
        else:  
          tgt = taskCache[tgtKey]
          affectedTasks[tgtKey] = tgt
        for (myArgs,inKey) in tgt.sourceLinks[linkKey]:
          myArgs[inKey] = val
    return affectedTasks
        

  # Workhorse of the task, called in parallel mode where applicable.
  def main(self,*args,**kwargs):
    # OVERRIDE ME
    return FancyArgs(*args,**kwargs)
    

  # Wrapper for main(). May be run on a worker process.
  def _main(self,workerName='main'):
    parentTask = global_taskManager.runningTask
    global_taskManager.runningTask = self
    self.finalizeInput()
    if self.logLevel & Log_Task: 
      self.log(FancyLog.logTask(self))
    if self.verbosity & Log_Task: 
      self.print( *FancyLog.printMessage(self,'Task started on worker {}.'.format(workerName)) )
      
    output = self.main(*self.myInput.args,**self.myInput.kwargs)
    self.myOutput = output if isinstance(output,FancyValue) else FancyValue(output)
    global_taskManager.runningTask = parentTask


  # Called when task is completed, to cleanup temporary files.
  def cleanup(self,taskCache):
    if not self.fancyClean: return
    (excludedFiles,excludedDirs) = self.fancyClean.cleanup(exclude=self.myOutput.tempfiles(),taskId=str(self))
    if self.parentId and (excludedFiles or excludedDirs):
      # Inherit tempfiles and tempdirs that could not yet be removed.
      try:
        parent = taskCache[self.parentId]
        if not parent.fancyClean: parent.fancyClean = FancyClean()
        parent.fancyClean.update(excludedFiles,excludedDirs)
      except KeyError:
        FancyReport.warning('Key "{}" not found in task cache while cleaning up {}.\nThe task cache contains {}.'.format(self.parentId,global_taskManager.taskCache.values()))
        
  def print(self,s,taskId=None,c='1;30'):
    global_taskManager.print(s,taskId or str(self),c)

  def log(self,data,taskId=None):
    global_taskManager.log(data,taskId or str(self))

  # Typically called as MyTask.fromCommandLine().run()
  def run(self,saveAs=None):
    if global_taskManager is None: raise RuntimeError('TaskManager not ready. To run a task use task.runFromCommandLine().')
    global_taskManager.run(self,saveAs)
    return self
#endclass

class FancyTaskInstance(FancyTask):
  def __init__(self,main):
    # Called when decorating a function with @FancyTask
    FancyTask.__init__(self)
    self.main = main.__get__(self,self.__class__)
    self.name = main.__name__


class FancyExec(FancyTask):
  """ 
  Extended class for tasks that execute jobs outside of Python,
  with a pre-defined main method.
  """
  runParallel = True
  myEnv = None
  myCwd = None
  myProg = None
  stdout = ''
  
  def getCommandLine(self):
    try:
      cmd = self.getCommand(*self.myInput.args,**self.myInput.kwargs)
      return ' '.join([str(v) for v in cmd])
    except:
      return FancyTask.getCommandLine(self)

  # set environment variables
  def setEnv(self,env):
    self.myEnv = env
    return self
    
  # set current working directory
  def setCwd(self,cwd):
    self.myCwd = cwd
    return self
    
  def setProg(self,prog):
    self.myProg = prog
    if not self.name: self.name = prog
    return self
  
  def setTitle(self,title):
    self.title = title
    return self
    
  def getCommand(self,*args,**kwargs):
    cmd = [self.myProg] if self.myProg else []
    cmd.extend([str(v) for v in args]);
    for k,v in kwargs.items(): cmd.extend([str(k),str(v)])
    return cmd

  def returnValue(self):
    # Return the inputs, this is useful when an input represents the name of an output file.
    return self.myInput

  def main(self,*args,**kwargs):
    cmd = self.getCommand(*args,**kwargs)
    opts = dict(shell=False, stderr=subprocess.STDOUT)
    if self.myCwd: opts['cwd'] = self.myCwd
    if self.myEnv: opts['env'] = self.myEnv
    #try:
    self.stdout = subprocess.check_output(cmd, **opts).decode('utf-8')
    #except subprocess.CalledProcessError as e:
    #  raise RuntimeError(
    #    'message',str(e),
    #    'type',e.__class__.__name__,
    #    'output',e.output,
    #    'traceback',FancyReport.traceback()
    #  )
    if (self.stdout):
      if (self.logLevel & Log_Output): 
        self.log(FancyLog.logMessage(self,'stdout',self.stdout.split('\n')))
      if (self.verbosity & Log_Output): 
        self.print(FancyLog.printMessage(self, self.stdout.split('\n')[0].substr(0,80)),'stdout')
    return self.returnValue()
#endclass


class FancyRequestItem(FancyTask):
  """ 
  Used to request a list- or dictionary-item from a FancyRequest.
  """
  def main(self,output,key):
    return output[key]


# Basic task manager that runs tasks in serial mode.
class TaskManager():
  runningTask = None # the main() function of this task is currently executing
  taskCache = odict()
  
  def __init__(self):
    pass
        
  def print(self,s,taskId=None,c='1;30'):
    if taskId: print('\033[{}m<{}>\033[0m {}'.format(c,taskId,s))
    else: print(s)

  def log(self,logItem,taskId=None):
    self.fancyLog.appendLog(logItem)
    
  # Submit pending tasks
  def submit(self,tasks):    
    self.taskCache.update(tasks)
    for key,task in tasks.items():
      if task.runStatus == Task_ResolvingInput:
        if task.alwaysRunMain: 
          task._main()
        if task.runStatus == Task_ResolvingInput and task.myInput.ready():
          task.runStatus = Task_Submitted
          self.onInputReady(task)
      elif task.runStatus == Task_ResolvingOutput and task.myOutput.ready():
        self.onOutputReady(task)

  # Act when the input of a task has been resolved
  def onInputReady(self,task):
    try:
      # carry out the task
      task._main()
      # output may contain unresolved subtasks (=pending tasks)
      self.onAfterMain(task)
    except (KeyboardInterrupt, SystemExit):
      raise
    except BaseException as e:
      if task.abortOnError:
        raise
      else:
        self.onOutputReady(task,FancyReport.errorTrace(e))
  
  def onAfterMain(self,task):
    # Forget myInput to release memory
    task.myInput = FancyArgs()
    task.runStatus = Task_ResolvingOutput
    pendingTasks = task.initRequests(task.myOutput)
    if pendingTasks: self.submit(pendingTasks)
    else: self.onOutputReady(task)
              
  # Act when the output of a task has been resolved
  def onOutputReady(self,task,errorTrace=None):
    self.taskCache.pop(str(task))
    if errorTrace:
      task.runStatus = Task_Failed
      if self.logLevel: self.log(FancyLog.logError(task,errorTrace))
      if self.verbosity: self.print( *FancyLog.printError(task,errorTrace) )
    else:
      task.runStatus = Task_Completed
      if task.myOutput:
        if self.logLevel & Log_Output: 
          self.log(FancyLog.logMessage(task,'output',task.myOutput.jsonify(summarize=True)))
        if self.verbosity & Log_Output: 
          self.print( *FancyLog.printMessage(task,task.myOutput.jsonify(summarize=True),'output') )
      task.cleanup(self.taskCache)
      affectedTasks = task._fulfillRequests(self.taskCache)
      self.submit(affectedTasks)
    task.myOutput = None
    
  # Run until completion of all pending tasks.
  def resolve(self,pendingTasks):
    self.submit(pendingTasks)
#endclass


# Task manager that runs inside worker.
class WorkerTaskManager(TaskManager):
  worker = None
  runningTask = None # the main() function of this task is currently executing
  
  def __init__(self,worker):
    self.worker = worker
    
  def print(self,s,taskId,c='1;30'):
    if not taskId: taskId = self.runningTask and str(self.runningTask);    
    # send result to main thread
    self.worker.putResult(Result_Print,(s,c),taskId)
    
  def log(self,data,taskId):
    if not taskId: taskId = self.runningTask and str(self.runningTask);    
    # send to main thread
    self.worker.putResult(Result_Log,data,taskId)
#endclass


# TaskManager that supports running tasks in parallel or distributed mode.
class FancyTaskManager(TaskManager):
  inputs = odict(
    'workDir', dict( default=None,
      help='Directory to store intermediate and final results. Default: subfolder of system tempdir.'
    ),
    'logDir', dict( default=None,
      help='Directory to store logFile (fancylog.js + fancylog.html) and attachments. Default: workDir.'
    ),
    'logLevel', dict( type=int, default=7,
      help='Detail level for logging to json/html file, 0 disables logging, 1 logs progress, 2 logs task input, 3 logs task output. Default: 7'
    ),
    'verbosity', dict( type=int, default=7,
      help='Detail level for printing messages to the console, 0 disables console logging, 1 logs progress, 2 logs task input, 3 logs task output. Default: 7'
    ),
    'doCleanup', dict( action='store_true', default=False,
      help='Automatically remove intermediate result files. Default: False (keep everything).'
    ),
    'tryResume', dict( action='store_true', default=False,
      help='Try to resume pipeline by reusing previous intermediate result files. Default: False.'
    ),
    'workerType', dict( type=assertMatch('([pPtT])'), default=('P'),
      help='Either "T" or "P": T uses multi-threading while P uses multi-processing. Default: P'
    ),
    'numWorkers', dict( type=assertType(int), default='auto',
      help='Number of parallel workers. Default: number of logical CPUs.'
    ),
    'jobServer', dict( type=assertJobServer, default=False,
      help='Address (ip-address:port) of job server started with "python fancyserver.py -auth=abracadabra"'
    ),
    'jobAuth', dict( default='abracadabra',
      help='Authorization key for submitting jobs to the job manager. Default: abracadabra.'
    )
  )
  workerPool = None
  workDir = None
  jobId = '0'
  
  def __init__(self,fancyReport,workDir=None,logDir=None,logLevel=7,verbosity=7,doCleanup=False,tryResume=False,workerType='P',numWorkers=0,jobServer=None,jobAuth='',fancyConfig=None):
    # reporting (captures output if jsonrpc2 is set)
    self.report = fancyReport

    # storage
    self.workDir = workDir if workDir else op.join(tempfile.gettempdir(),'FancyWork')
    self.doCleanup = doCleanup
    self.tryResume = tryResume
    
    # logging
    self.fancyLog = FancyLog(logDir, tryResume)
    self.logLevel = logLevel
    self.verbosity = verbosity

    # parallel processing
    self.jobServer = jobServer
    self.jobAuth = jobAuth
    self.numWorkers = numWorkers
    self.workerType = workerType
    if jobServer:
      self.workerPool = RemotePool(jobServer,jobAuth)
    elif numWorkers>0:
      self.workerPool = LocalPool(numWorkers,workerType)
    self.jobCount = 0

    # configuration file
    self.fancyConfig = fancyConfig
    
    TaskManager.__init__(self)
    
    # make available to tasks via global variable
    global global_taskManager
    global_taskManager = self

  @staticmethod
  def _extendParser(p,inputs):
    for key in inputs:
      inp = inputs[key].copy()
      short = inp.pop('short') if 'short' in inp else key.lower()
      positional = inp.pop('positional') if 'positional' in inp else False
      dest = [key] if positional else ['-{}'.format(short),'--{}'.format(key)]
      # ignore argument default, defer to parseInputs
      if 'default' in inp: del inp['default']
      # overwrite argument type, defer to parseInputs
      if 'type' in inp: inp['type'] = str
      p.add_argument(*dest,**inp)
    
  @classmethod
  def _getParser(cls,TaskToRun):
    p = argparse.ArgumentParser(
      description=TaskToRun.description if TaskToRun.description else TaskToRun.title,
      formatter_class=argparse.ArgumentDefaultsHelpFormatter,
      argument_default=argparse.SUPPRESS,
      conflict_handler='resolve'
    )
    g = p.add_argument_group('TaskManager arguments')
    cls._extendParser(g,FancyReport.inputs)
    cls._extendParser(g,cls.inputs)
    g = p.add_argument_group('{} module arguments'.format(TaskToRun.__name__))
    cls._extendParser(g,TaskToRun.inputs)
    return p

  # Run a task, and report either the result or errors.
  def run(self,task,saveAs=None):
    try:
      self.runningTask = task
      output = task.getOutput()
      self.report.success(output)
      if saveAs:
        if op.dirname(saveAs) == '': saveAs = task.tempfile(saveAs)
        with open(saveAs,'w') as fp:
          json.dump(FancyReport.jsonify(output),fp)
    except BaseException as e:
      if task.abortOnError:
        self.report.fail('Fatal error in task {}.'.format(task))
      else:
        errorTrace = FancyReport.errorTrace(e)
        errorTrace['message'] = [
          'Fatal error in task {}.'.format(task),
          errorTrace['message']
        ]
        self.log(task,errorTrace,name='Fatal error',tp='error')

  # Act when all input requests of a task are resolved
  def onInputReady(self,task):
    if self.workerPool and task.runParallel:
      # Send task to worker pool
      self.workerPool.putTask(task)
      self.jobCount += 1
    else:
      TaskManager.onInputReady(self,task)

  # Run until completion of all pending tasks.
  def resolve(self,pendingTasks):
    self.jobCount = 0
    self.submit( pendingTasks )
    while self.jobCount > 0:
      resultCode,resultData,taskId,workerName = self.workerPool.getResult()
      if resultCode is Result_Success:
        myOutput,fancyClean = resultData
        self.jobCount -= 1
        task = self.taskCache[taskId]
        task.myOutput = myOutput
        if fancyClean:
          task.fancyClean = fancyClean
        self.onAfterMain(task)
      elif resultCode is Result_Failed:
        runningTask,errorTrace = resultData
        errorTrace['message'] = [
          'Worker {} encountered an error while running task {}.'.format(workerName,taskId),
          errorTrace['message']
        ]
        self.jobCount -= 1
        task = self.taskCache[taskId]
        self.onOutputReady(task,errorTrace)
      elif resultCode is Result_Print:
        s,c = resultData        
        self.print(s,taskId,c)
      elif resultCode is Result_Log:
        self.log(resultData,taskId)
        

## Worker class used for parallel task execution.
class Worker():
  runId = None
  
  def __init__(self, jobQueue, resultQueue):
    self.jobQueue = jobQueue
    self.resultQueue = resultQueue
    
  def getTask(self):
    return self.jobQueue.get()
    
  def putResult(self,resultCode,resultData,taskId):
    result = (resultCode,resultData,taskId,self.name)
    self.resultQueue.put(result)

  def run(self):
    global global_taskManager
    task = None
    resultCode = None
    resultData = None
    while True:
      try:    
        global_taskManager = WorkerTaskManager(self)
        task,self.runId = self.getTask()
        if task is None:
          self.print('No task, exiting worker {}.'.format(self.name))
          break
        task._main(self.name)
        resultCode = Result_Success
        resultData = (task.myOutput,task.fancyClean)
      except BaseException as e:
        resultCode = Result_Failed
        resultData = (global_taskManager.runningTask,FancyReport.errorTrace(e))
      finally:
        self.putResult(resultCode,resultData,str(task) if task else None)        
        # empty memory
        task = None
        resultCode = None
        resultData = None
        global_taskManager = None
        unreachable = gc.collect()
#endclass


class RemoteWorker(Worker,multiprocessing.Process):
  def __init__(self, managerAddr,managerAuth):
    multiprocessing.Process.__init__(self)
    from multiprocessing.managers import BaseManager
    class ManagerProxy(BaseManager): pass
    ManagerProxy.register('getJobQueue')
    ManagerProxy.register('getResultQueue')
    ManagerProxy.register('getControlQueue')
    print('Connecting to job server {}:{}'.format(managerAddr[0],managerAddr[1]))
    self.manager = ManagerProxy(address=managerAddr,authkey=managerAuth)
    self.manager.connect()
    self.jobQueue = self.manager.getJobQueue()

  def getTask(self):
    return pickle.loads(self.jobQueue.get())
    
  def putResult(self,resultCode,resultData,taskId):
    result = (resultCode,resultData,taskId,self.name)
    resultQueue = self.manager.getResultQueue(self.runId)
    resultQueue.put(pickle.dumps(result))
#endclass


class WorkerThread(Worker,threading.Thread):
  def __init__(self, jobQueue, resultQueue):
    threading.Thread.__init__(self)
    Worker.__init__(self,jobQueue,resultQueue)
#endclass


class WorkerProcess(Worker,multiprocessing.Process):
  def __init__(self, jobQueue, resultQueue):
    multiprocessing.Process.__init__(self)
    Worker.__init__(self,jobQueue,resultQueue)
#endclass
    
    
## Maintains a pool of worker threads for workerType T,
## or a pool of worker processes for workerType P.
class LocalPool():
  def __init__(self,numWorkers,workerType):
    self.queueClass = queue.Queue if workerType=='T' else multiprocessing.Queue
    workerClass = WorkerThread if workerType=='T' else WorkerProcess
    self.jobQueue = self.queueClass()
    self.resultQueue = self.queueClass()
    for w in range(numWorkers):
      worker = workerClass(self.jobQueue,self.resultQueue)
      worker.daemon = True
      worker.start()

  def putTask(self,task):
    self.jobQueue.put((task,None))
    
  def getResult(self):
    return self.resultQueue.get()
#endclass


## Connects to a remote pool of workers, started by fancymanager.py,
class RemotePool():
  resultQueue = None
  
  def __init__(self,jobServer,jobAuth):
    self.runId = uuid.uuid4()
    class ManagerProxy(multiprocessing.managers.BaseManager): pass
    ManagerProxy.register('getJobQueue')
    ManagerProxy.register('getResultQueue')
    ManagerProxy.register('popResultQueue')
    ManagerProxy.register('getControlQueue')
    print('Connecting to job server {}:{}.'.format(jobServer[0],jobServer[1]))
    self.manager = ManagerProxy(address=jobServer,authkey=jobAuth)
    self.manager.connect()
    multiprocessing.current_process().authkey = jobAuth
    self.jobQueue = self.manager.getJobQueue()
    self.resultQueue = self.manager.getResultQueue(self.runId)
    
  def putTask(self,task):
    self.jobQueue.put(pickle.dumps((task,self.runId)))
  
  def getResult(self):
    return pickle.loads(self.resultQueue.get())

  def getControlQueue(self):
    return selfmanager.getControlQueue(self.runId)

  def __del__(self):
    if self.resultQueue: self.manager.popResultQueue(self.runId)
#endclass
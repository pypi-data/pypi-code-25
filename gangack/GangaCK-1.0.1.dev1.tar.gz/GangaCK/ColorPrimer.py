
"""

ColorPrimer centralize the management of colorful things in GangaCK.

Color is a string-ready for `.format()` call.

Example: 

>>> import ColorPrimer
>>> ColorPrimer.green     # invoking __repr__
green
>>> print ColorPrimer.green    # invoking __str__
\033[31;32m{0}\033[00m
>>> print ColorPrimer.green.format('some text')
\x1b[31;32msome text\x1b[00m

Color by status:

>>> ColorPrimer.status('completed')
blue
>>> ColorPrimer.status('completed', grey_completed=True)   # Alternate repr of success jobs
grey
>>> ColorPrimer.status('running')
green

Color by backend:

>>> ColorPrimer.backend('Dirac')
blue
>>> ColorPrimer.backend('Interactive')
magenta

Color by humansize:

>>> ColorPrimer.humansize('10.2 TB')
red
>>> ColorPrimer.humansize('120 GB')
red
>>> ColorPrimer.humansize('99 GB')
yellow
>>> ColorPrimer.humansize('25 MB')
normal
>>> ColorPrimer.humansize('1.41 KB')
grey

Printing color legends:

>>> ColorPrimer.print_status_color_legend()
STATUS :  ...
>>> ColorPrimer.print_backend_color_legend()
BACKEND:  ...

See also:

    http://en.wikipedia.org/wiki/ANSI_escape_code

"""

# from . import *

class LabeledString(str):
  """
  Just like regular string, but with customized repr for better debugging & testing.
  """
  def __new__(self, label, val):
    obj = str.__new__(self, val)
    obj._label = label
    return obj
  def __repr__(self):
    return self._label


normal    = LabeledString( 'normal'   , "\033[10;10m{0}\033[00m")
grey      = LabeledString( 'grey'     , "\033[31;30m{0}\033[00m")
red       = LabeledString( 'red'      , "\033[31;31m{0}\033[00m")
green     = LabeledString( 'green'    , "\033[31;32m{0}\033[00m")
yellow    = LabeledString( 'yellow'   , "\033[31;33m{0}\033[00m")
blue      = LabeledString( 'blue'     , "\033[31;34m{0}\033[00m")
magenta   = LabeledString( 'magenta'  , "\033[31;35m{0}\033[00m")
cyan      = LabeledString( 'cyan'     , "\033[31;36m{0}\033[00m")
white     = LabeledString( 'white'    , "\033[31;37m{0}\033[00m")
bgwhite   = LabeledString( 'bgwhite'  , "\033[47;30m{0}\033[00m")
bgyellow  = LabeledString( 'bgyellow' , "\033[43;30m{0}\033[00m")


#------------------------------------------------------------------------------


STATUS_COLOR = {
  'new'       : white,
  'submitting': yellow,
  'submitted' : bgyellow,
  'running'   : green,
  'completing': magenta,
  'completed' : blue,
  'failed'    : red,
  'killed'    : grey,
}

BACKEND_COLOR = {
  'PBS'         : yellow,
  'LSF'         : yellow,
  'Interactive' : magenta,
  'Dirac'       : blue,
  'Local'       : yellow,
}

def status(st, grey_completed=False):
  return grey if st=='completed' and grey_completed else STATUS_COLOR[st]

# def get_status_color(st, grey_completed=False):
#   logger.warning('Depreciate me')
#   return status(st, grey_completed)

def backend(val):
  return BACKEND_COLOR[str(val)] # Use str in some case where DictTree instance is used.

def humansize(val):
  val = str(val)
  if 'TB' in val:
    return red 
  elif 'GB' in val:
    if float(val.split()[0]) > 100:
      return red
    else:
      return yellow
  elif 'MB' in val:
    return normal
  return grey


def print_status_color_legend():
  print "STATUS : ",
  for st in sorted(STATUS_COLOR):
    print status(st).format(st),
  print 

def print_backend_color_legend():
  print "BACKEND: ",
  for x in sorted(BACKEND_COLOR):
    print backend(x).format(x),
  print 

## Given the conversion char, return the function responsible for color-making
## These colorizer names MUST exists also as Job's attribute
CONVERSION_PARAM = {
  's': status,
  'b': backend,
  'h': humansize,
}

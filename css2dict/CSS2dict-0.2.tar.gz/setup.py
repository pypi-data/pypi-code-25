from distutils.core import setup

long_desc = '''
CSS2dict is a Python module to parse CSS and make it a dictionary
Features:
 - It is callable, that means you can do directly CSS2dict(code) instead of doing CSS2dict.parse(code)
 - It returns a dictionary of this structure:
´´´
    {
    'selector':
        {
        'selection': <Style object>
        }
    'other selector:
        {
        'selection': <Style object>
        'other selection': <Style object>
        }
    }
´´´
 - Style objects are objects containing all the properties of the selection, like selection.color, selection.font-size, etc.
 - Style objects have a __str__ method wich makes them look as dictionaries, but they aren't
 - If you want Style objects to be dictionaries, you can pass True as the second argument

    >> import CSS2py
    >> x = CSS2py(".marquee { color: red}")
    >> x['.']['marquee'].color
    red
    >> type(x['.']['marquee'])
    Style
    >> x
    {'.':{'marquee':{'color':'red'}}}
    
'''
setup(
  name = 'CSS2dict',
  packages = ['CSS2dict'], # this must be the same as the name above
  version = '0.2',
  description = 'A module to convert CSS code into a Python dictionary',
  long_description = long_desc,
  author = 'FranchuFranchu',
  author_email = 'udontcare@gmail.com',
  url = 'https://github.com/FranchuFranchu/CSS2dict', 
  download_url = 'https://github.com/FranchuFranchu/CSS2dict/archive/0.1.tar.gz', 
  keywords = ['python', 'CSS', 'dictionary'], # arbitrary keywords
  classifiers = [],
)
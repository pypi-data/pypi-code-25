import os
import sys
import copy
import re
import yaml
import cam
from cam.enums import Platform,Architecture
from cam.sysinfo import PLATFORM,ARCH
from cam.errors import FatalError
from cam.interpreter import Interpret #,Compile,IsConst

_TOOL_MAP={
    'cmake':'CMakeLists.txt',
    'node-gyp':'binding.gyp'
}

class Object(object):
    def __ini__(self):
        pass

PUBLIC= [
        'name','version','tool','msvs','arch','platform',
        'location','build_dir','cache_dir','install_prefix','steps',
        '__file__','__directory__'
    ]
STEPs=['fetch','configure','make','cpplint','install','package','test']
OPTIONS=[ 'debug']
PROPERTIES = ['patches','origin', 'enviroment']
PROPERTIES = PUBLIC + STEPs



_VAR_PATTERN = re.compile(r'\$\{(?P<class>[A-Za-z]\w*\.)?(?P<var>[A-Za-z_]\w*)\}')
def IsConst(expr):
    ret = _VAR_PATTERN.findall(expr)
    return  len(ret) == 0

def Compile(string, vtable, clone = False):
    def _replace(matched):
        klass = matched.group('class')
        var   = matched.group('var')
        if klass:
            klass = klass[:-1]
        obj = vtable.get(klass,{})
        if var in obj:
            return obj[var]
        return matched.group()
    if clone:
        return _VAR_PATTERN.sub(_replace,string)
    else:
        string = _VAR_PATTERN.sub(_replace,string)
        return string


def _make_ctalbe( config, gc= None):

    gctable={}
    if gc is not None:
        for name in PUBLIC:
            gctable[name] = getattr(gc,name)
    ctable={}
    for name in PUBLIC:
        ctable[name] = getattr(config,name,None)
    return {None:ctable,'gc':gctable}

    
def _CompilePublic( config , gc = None):

    gctable={}
    if gc is not None:
        for name in PUBLIC:
            gctable[name] = getattr(gc,name)

    vtable={}
    ctable={}
    names=[]
    for name in PUBLIC:
        val = getattr(config,name,None)
        if isinstance(val,str):
            if IsConst(val):
                ctable[name] = val
            else:
                vtable[name] = val
                names.append(name)
    n = len(vtable)
    
    while n :
        n -=1
        for name, val in vtable.items():
            val = Compile(val, {None:ctable,'gc':gctable})
            if IsConst(val):
                ctable[name] = val
                vtable.pop(name)
                break
    if len(vtable):
        raise FatalError('interpreter general config failed.')
    for name in names:
        setattr( config, name, ctable[name])


def _CompileOrigin( origin ,config, gc):
    if origin is None:
        return
    obj = Object()
    ctable = _make_ctalbe(config,gc)
    for names in [['git','commit'],['tarball','dir','format']]:
        for name in names:
            if name in origin:
                val = Compile( origin[name], ctable)
                setattr(obj,name,val)
        
    return obj

def _CompileEnviroment(envs, config, gc):
    if envs is None:
        return
    enviroment={}
    ctable = _make_ctalbe(config,gc)
    type = None
    for name , val in envs.items():
        if isinstance(val,str):
            val = Compile(val,ctable)
        if isinstance(val,dict):
            for k, v in val.items():
                type = k
                val = Compile(v,ctable)
                break
        enviroment[name]={
            'type':type,
            'value': val
        }    
    return enviroment
        

        

class Config(object):
    tool       = None
    enviroment = None
    origin     = None
    debug      = False
    patches    = []
    steps      = ['configure','make']
    location   = '${__directory__}'
    build_dir  = '${location}/build'
    cache_dir  = '${__directory__}/build/.cache'
    install_prefix = '${__directory__}/dist/${platform}/${arch}'
    msvs     =  2017
    arch     =  ARCH
    platform =  PLATFORM


    def __init__(self, config, gc = None):
        
        self.general = gc
        self._config = config
        for name in PROPERTIES:
            if not getattr(self,name,None):
                setattr(self,name,None)
        
        # init gernal config
        if gc is None:
            self._make_me_general()
        else:
            self._make_me_project()
        #guess tool
        if not self.tool:
            if self.general and self.general.tool:
                self.tool = self.general.tool
            else:
                for name , filename in _TOOL_MAP.items():
                    path = os.path.join(self._config['__directory__'],filename)
                    if os.path.isfile( path):
                        self.tool = name

        _CompilePublic( self, gc )
        if 'origin' in self._config:
            self.origin = _CompileOrigin( self._config['origin'],self, gc)
        if 'enviroment' in self._config:
            self.enviroment = _CompileEnviroment( self._config['enviroment'], self,gc )

        for name in STEPs:
            val = self._makestep( name)
            setattr(self,name,val)

    def _make_me_general(self):
        for name in PROPERTIES:
            val = self._config.get(name,None)
            if val:
                setattr(self,name, val )

    def _make_me_project(self):
        self.name = self._config.get('name',None)
        self._overwrite(self.general)
        self._overwrite(self._config, False)
        if self._config.get('location',None)  is None:
            self.location ='${__directory__}/build/${name}-${version}-${platform}-${arch}'
        if self._config.get('build_dir',None)  is None:
            self.build_dir ='${location}/build'


    def _overwrite(self, config, public_only = True):
        props = PUBLIC
        if not public_only:
            props = PUBLIC + STEPs
        for name in props:
            if isinstance(config,dict):
                val = config.get(name,None)
            elif isinstance(config,Config):
                val = getattr(config,name)
            if val :
                setattr(self,name,val)

    def _makestep(self,name):

        handlers ={
            'before': None,
            'entry': None,
            'after': None,
            'enviroment': None,
            'option': None,
        }
        value = getattr(self,name,None)
        if value is None:
            return handlers

        cmds =[]

        for item in value:
            if isinstance( item,dict):                
                for name, val in item.items():
                    if name == '.before':
                        handlers['before'] = val
                    elif name == '.after':
                        handlers['after'] = val
                    elif name == '.enviroment':
                        handlers['enviroment'] = val
                    elif name == '.option':
                        handlers['option'] = val

                    else:
                        cmds.append(item)
            else:
                cmds.append(item)

        if cmds:
            handlers['entry'] = cmds

        if handlers['enviroment']:
            handlers['enviroment'] = _CompileEnviroment( handlers['enviroment'], self,self.general)
        return handlers


_ASSIGN_EXPR_PATTERN = re.compile(r'\s*(?P<name>[A-Za-z]\w*)\s*=\s*(?P<var>(\S+|\S[ \S]+\S))\s*$')

def _LoadConfigFile(filename, options):
    config ={}
    if options is None:
        options = []

    
    if filename is None:
        config['__file__']      = os.path.abspath( os.getcwd() + '/$' )
        config['__directory__'] = os.path.abspath( os.getcwd() )
        config['location']      = config['__directory__']
    else:
        path = os.path.abspath(filename)
        config = yaml.load( open(path) )
        config['__file__']      = os.path.abspath( path )
        config['__directory__'] = os.path.dirname(config['__file__'])
        if not config.get('location',None):
            config['location'] = config['__directory__'] 

    for opt in options:
        m = _ASSIGN_EXPR_PATTERN.match( opt )
        if m is None:
            raise FatalError('invald set expr : %s'%opt)
        name = m.group('name')
        val  = m.group('value')
        if name in PUBLIC:
            config[name] = val

    return config

def Load(filename = None, options=[]):

    config = _LoadConfigFile(filename,options)

    # general config (name = None), the first one
    gc = Config(config, None)
    projects = config.get('projects',None)
    if projects is None:
        return [gc]
    else:
        prjs=[]
        for item in projects:
            for name , prj in item.items():
                prj['name'] = name
                prjs.append( Config(prj,gc) )
        return prjs






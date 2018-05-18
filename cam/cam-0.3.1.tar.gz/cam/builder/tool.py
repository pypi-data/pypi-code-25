
import os
import glob
import subprocess

from cam.enums import Platform,Architecture
from cam.errors import FatalError
from cam.utils import console
from cam.utils.console import call as Call
from cam.command import Exec
from cam.source import Git, Tarball

def _msvs_ver(year):
    if type(year) == type(''):
        year = int(year)
    ver={
        2017 : '15',
        2015 : '14',
        2012 : '11',
        2010 : '10',
        2008 : '9',
        2005 : '8'
    }
    return ver.get(year,None)

def _Exec(script, config,stream=None):
    cmds = script
    if not isinstance(script,list):
        cmds = [script]
    for cmd in cmds:
        Exec(cmd,config,config.build_dir,stream)

class Base(object):
    def __init__(self,config):
        self.config = config
        self.environs =[]

    def _stepitem(self,name):
        step = getattr(self.config,name)
        return step['before'] ,step['entry'],step['after'],step['enviroment']
    

    def _modify_env(self,name,environ):
        type = environ['type']
        val  = environ['value']

        if type is None:
            os.environ[name] = val

        elif type in ['path','path+','+path']:
            path = os.path.normpath(val).replace("\\",'/')
            old  = os.environ.get(name,None)
            sep = ':'
            if self.config.platform == Platform.WINDOWS:
                sep = ';'
            if old is None or type == 'path':
                os.environ[name] = path
            elif type == 'path+':
                os.environ[name] = old + sep + path
            elif type == '+path':
                os.environ[name] = path + sep


    def _pushenv(self, evars):
        '''
        modify current enviroment accroding env
        '''
        
        #save old one
        self.environs.append(os.environ.copy())
        for name, val in evars.items():
            self._modify_env(name,val)


    def _popenv(self):
        if len(self.environs) == 0:
            return
        env = self.environs.pop()
        diff = set(os.environ.keys()).difference(set(env.keys()))
        for name in diff:
            del os.environ[name]
        for name ,val in env.items():
            os.environ[name] = val
        return env

    def _exec(self,name,stream):
        gc = self.config.general
        before, entry,after, enviroment = self._stepitem(name)

        fn = getattr(self,name,None)
        if not entry and not fn:
            raise FatalError("%s was not implement."%name)

        #load general enviroment
        if gc and gc.enviroment:
            self._pushenv(gc.enviroment)
        if self.config.enviroment:
            self._pushenv(self.config.enviroment)
        if enviroment:
            self._pushenv(enviroment)

        try:
            if before:
                _Exec( before, self.config, stream )

            if entry:
                _Exec( entry, self.config, stream )
            else:
                fn = getattr(self,name)
                fn(stream)
            if after:
                _Exec( after, self.config, stream )
        except :
            raise FatalError("exec <%s> failed"%name)

        finally:
            if enviroment:
                self._popenv()

            if self.config.enviroment:
                self._popenv()
                
            if gc and gc.enviroment:
                self._popenv()

    def fetch(self,stream):
        origin = self.config.origin
        if not origin:
            raise FatalError('no default fetch step implement')

        fetcher = None

        if hasattr(origin,'git'):
            fetcher = Git( self.config)
        elif hasattr(origin,'tarball'):
            fetcher = Tarball( self.config)
        else:
            raise FatalError( 'can not find the fetch.')
            
        fetcher.fetch()
        fetcher.extract()

    def cpplint(self,stream):
        option = self.config.cpplint['option']
        if option is None:
            option = {}

        filters  = option.get('filter',[])
        linelength  = option.get('linelength',None)
        sources  = option.get('sources',[])
        directory = self.config.location
        options = ''
        if len(filters):
            options +=" --filter=" + ",".join(filters)
        if linelength!=None:
            options +=" --linelength=" + str(linelength)
        slist=[]
        for src in sources:
            rex = os.path.join(self.config.location,src)
            slist +=glob.glob(rex)
        for filename in slist:
            try:
                Call('python -m cpplint %s %s'%(options,filename),directory,stream)
            except subprocess.CalledProcessError:
                raise FatalError('cpplint failed at %s'%filename)

    def run(self,step, stream):
        if step == 'cpplint':
            self.cpplint(stream)
            return
        self._exec( step,stream)


class CMake(Base):


    def __init__(self, config):
        Base.__init__(self,config)
    
    def _config_options(self):
        arch = self.config.arch
        if arch == Architecture.X86:
            arch = 'win32'
        elif arch == Architecture.X86_64:
            arch = 'x64'

        build_type = 'Release'
        if self.config.debug:
            build_type = 'Debug'

        return ' --config %s -- /p:Platform=%s'%(build_type,arch)


    def configure(self, stream = None):
        command   = 'cmake '
        msvs      = self.config.msvs
        arch      = self.config.arch
        platform  = self.config.platform
        location  = self.config.location
        build_dir = self.config.build_dir
        install_prefix = self.config.install_prefix
        ver = _msvs_ver(msvs)
        if ver is None:
            raise FatalError('unsupport msvs %d'%self.config.msvs)

        if platform == Platform.WINDOWS:
            if arch == Architecture.X86_64:
                arch = 'Win64'
            elif arch == Architecture.X86:
                arch = 'x86'
            
            command += ' -G"Visual Studio %s %d %s" '%(ver,msvs,arch)
            command += ' -DCMAKE_INSTALL_PREFIX=%s'%install_prefix
            CMAKE_CONFITURE_OPTIONS = os.environ.get('CAMKE_CONFITURE_OPTIONS',None)
            if isinstance( CMAKE_CONFITURE_OPTIONS, str):
                command += ' %s '%CMAKE_CONFITURE_OPTIONS

        command += ' %s'%location
        Call( command,build_dir ,stream)


    def make(self, stream = None):
        build_dir = self.config.build_dir
        command = 'cmake --build . --target ALL_BUILD '
 
        command += self._config_options()
        Call( command,build_dir ,stream)

    def install(self,stream = None):
        command = 'cmake --build . --target INSTALL '
        command += self._config_options()
        Call( command,self.config.build_dir ,stream)
    
    def test(self,stream = None):
        command = 'cmake --build . --target RUN_TESTS '
        command += self._config_options()
        Call( command,self.config.build_dir ,stream)


    def clean(self,stream = None):
        command = 'cmake --build . --target ALL_BUILD '
        command += self._config_options()
        command += ' /t:clean'
        Call( command,self.config.build_dir ,stream)


class NodeGyp(Base):
    def __init__(self, config):
        Base.__init__(self,config)
    
    def _config_options(self):
        arch = 'x64'
        if self.config.arch == Architecture.X86:
            arch = 'win32'
        elif self.config.arch == Architecture.X86_64:
            arch = 'x64'

        build_type = 'Release'
        if self.config.debug:
            build_type = 'Debug'

        return ' --config %s -- /p:Platform=%s'%(build_type,arch)


    def configure(self, stream = None):
        msvs      = self.config.msvs
        arch      = self.config.arch
        platform  = self.config.platform
        location  = self.config.location

        command = 'node-gyp configure '
        if platform == Platform.WINDOWS:
            command += '--msvs_version=%d'%msvs
            
            if arch == Architecture.X86:
                arch = 'win32'
            elif arch == Architecture.X86_64:
                arch = 'x64'

            command += ' --arch=%s'%arch
            command += ' --directory=%s'%location
            directory = location

        Call( command,directory ,stream)


    def make(self, stream = None):
        location  = self.config.location
        command = 'node-gyp build'
        command += ' --directory=%s'%location
        if self.config.debug:
            command +=' options=--debug'
        Call( command,location ,stream)

    def clean(self,stream = None):
        location  = self.config.location        
        command = 'node-gyp clean'
        if self.config.debug:
            command +=' options=--debug'
        Call( command,location ,stream)

def BuildTool(config):
    tool = config.tool
    if tool == 'cmake':
        return CMake( config)
    elif tool == 'node-gyp':
        return NodeGyp( config )
    elif tool == 'custom':
        return Base(config)
    else:
        raise FatalError('Unsupported build tool %s'%tool)
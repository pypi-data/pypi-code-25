
import os
import copy
import re
from cam.command import Exec
from cam.builder.tool import BuildTool
from cam.errors import FatalError
from cam.utils import console
from cam.utils.console import OStream 
_STEPs = 'fetch','configure','make','cpplint','test','install','package'   
class Build(object):


#    def __init__(self,name, config, args):
    def __init__(self, config, args):
        self.name = config.name
        self.general = config.general
        self.config = config #copy.deepcopy(config)
#        self.configuration = config
        self.args = args
        self.success = []
        self.failure = None
        self.runing = None
        self.steps = []

        self._filter()

    def _filter(self):
        steps = []
        for step in _STEPs:
            if getattr(self.args,step):
                steps.append(step)
        if self.args.clean:
            assert( len( steps) == 0 )
            self.steps =['clean']
            return

        if not steps:
            steps = _STEPs
        
        for step in self.config.steps:
            if step in steps:
                self.steps.append(step)

    def run(self):
        build = BuildTool(self.config)

        flog = None

        for step in self.steps:
            if step in ['configure']:
                if not os.path.isdir(self.config.build_dir):
                    os.makedirs(self.config.build_dir)

            logd = self.args.log_dir
            if logd:
                filename = os.path.join( logd,
                '%s-%s-%s-%s.log'%(self.config.name,step,
                self.config.platform,self.config.arch))
                if not os.path.isdir(logd):
                    os.makedirs( logd)

                flog = open(filename,'w+')
                console.stdout = OStream(flog)
            else:
                console.stdout = OStream()

            try:
                msg = '%-10s : %sing'%(self.config.name,step) + ' ...'
                console.log( '\n'+console.Fore.CYAN + console.Back.WHITE + console.Style.DIM+
                    '  %-38s'%msg)

                build.run( step, console.stdout)
                self.success.append(step)
                
            except FatalError as e:
                self.failure = step
                raise FatalError('<%s> %s failed'%(self.config.name,step),e.trace)
            except:
                self.failure = step
                raise FatalError('<%s> %s failed'%(self.config.name,step))
            finally:
                if flog:
                    flog.close()
                

            

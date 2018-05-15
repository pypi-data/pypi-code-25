import uuid

from serpentarium.engine.Mod import Mod
from serpentarium.engine.ModContext import ModContext
from serpentarium.logging.LoggingUtil import LoggingUtil


class Greeter(Mod):

    def __init__(self, name: str, id: uuid, settings: dict, context: ModContext) -> None:
        super().__init__(name, id, settings, context)
        self._log = LoggingUtil.get_logger(self.__class__.__name__)

    def on_start(self) -> None:
        self._log.info("""
        
                    
                          __,                                                      _/     _                 /
                         (                          _/_         o                 /      //       /         /
                          `.  _  _    ,_   _  _ _   /  __,  _  ,  , , _ _ _      / __,  //  ,_   /_  __,  _/ 
                        (___)(/_/ (__/|_)_(/_/ / /_(__(_/(_/ (_(_(_/_/ / / /_    /(_/(_(/__/|_)_/ /_(_/(_/   
                                     /|                                                    /|                
                                    (/                                                    (/                 
 
                        """
                       )

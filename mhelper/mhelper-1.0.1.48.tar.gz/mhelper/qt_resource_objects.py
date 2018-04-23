import warnings


__author__ = "Martin Rusilowicz"


class ResourceIcon:
    """
    References a Qt resource.
    (Does not require the Qt library until :method:`icon` is called).
    """
    
    SEARCH = []
    CACHE = { }
    
    
    @classmethod
    def add_search( cls, text: str ):
        cls.SEARCH.append( text )
    
    
    def __init__( self, path: str ):
        """
        CONSTRUCTOR
        :param path: Resource path
        """
        self._path = path
        self._icon = None
    
    
    @property
    def path( self ):
        return self._path
    
    
    def __repr__( self ):
        return "ResourceIcon(«{0}»)".format( self._path )
    
    
    def __call__( self ):
        """
        Calls :method:`icon`.
        """
        return self.icon()
    
    
    def icon( self ):
        """
        Use to obtain the icon.
        """
        from PyQt5.QtGui import QIcon
        
        
        if not self._icon:
            cached = self.CACHE.get( self._path )
            
            if cached is not None:
                self._icon = cached
            else:
                from PyQt5.QtCore import QFile
                
                if ":" not in self._path:
                    final = None
                    for search in type( self ).SEARCH:
                        path = search.replace( "*", self._path )
                        if QFile.exists( path ):
                            final = path
                            break
                    
                    if final is None:
                        warnings.warn( "No such icon as «{}» given searches «{}».".format( self._path, type( self ).SEARCH ), UserWarning )
                        final = self._path
                else:
                    final = self._path
                
                self._icon = QIcon( final )
                self.CACHE[self._path] = self._icon
        
        return self._icon

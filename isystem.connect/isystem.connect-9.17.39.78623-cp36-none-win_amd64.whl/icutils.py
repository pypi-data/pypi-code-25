"""
This module is deprecated. Instead of using ICFactory class,
connect to winIDEA using class ConnectionMgr(). This way you have more
options to connect to the desired winIDEA instance.

Example:

import isystem.connect as ic

cmgr = ic.ConnectionMgr()
cmgr.connectMRU('')

dbg = ic.CDebugFacade(cmgr)


Old example:

from isystem import icutils

icFactory = icutils.getFactory()

dbg = icFactory.getDebugFacade()

"""

import isystem.connect

# For versioning see also http://www.python.org/dev/peps/pep-0008/,
# section 'Version bookkeeping'.
""" Contains version info about this product. """
__version__ = isystem.connect.getModuleVersion()

g_defaultFactory = None

# When called from winIDEA, workspaceFileName should be None,
# and winIDEAConnect() should be called on returned object.
def getFactory(workspaceFileName = ''):
    """
    This function is preferred method for instantiating ICFactory
    class. It always returns the same instance of ICFactory class
    connected to winIDEA.
    
    If more than one connection is required (for example in case of
    multi-core targets, other connections can be done by directly
    instantiating the ICFactory class.

    Returns: ICFactory connected to winIDEA instance
    
    See also: ICFactory.__init__() for detailed description of parameter.

    Example:
    --------

    from isystem import icutils

    icFactory = icutils.getFactory()

    dbg = icFactory.getDebugFacade()

    dbg.download()
    dbg.setBP('main')
    dbg.run()
    """
    global g_defaultFactory
    if (g_defaultFactory == None):
        g_defaultFactory = ICFactory(workspaceFileName)

    return g_defaultFactory


class ICFactory:
    """
    This class is deprecated. Instead of using it, connect to winIDEA
    using class ConnectionMgr(). This way you have more options to
    connect to the desired winIDEA instance.

    Example:

    import isystem.connect as ic

    cmgr = ic.ConnectionMgr()
    cmgr.connectMRU('')

    dbg = ic.CDebugFacade(cmgr)

    
    Old example using this class:

    from isystem import icutils

    icFactory = icutils.ICFactory('')

    debug = icFactory.getDebugFacade()
    debug.download()
    """
    __connectionMgr = None
    
    __debugCtrl = None
    __dataCtrl = None
    __projectCtrl = None
    __terminalDocCtrl = None
    __hilCtrl = None
    __ideCtrl = None
    __workspaceCtrl = None
    __coverageCtrl = None
    __profilerCtrl = None
    __testCaseCtrl = None

    def __init__(self, workspaceFileName = ''):
        """
        Instantiates this class and connects to winIDEA, depending on
        the values of parameter:
        
            If 'workspaceFileName == None', no connection is
            established. You should call 'connect()' before any other
            operation.

            If workspaceFileName == '' (empty string),
            connection is made to winIDEA with the most recently used
            workspace.

            If 'workspaceFileName == <workspaceFileName>',
            connection is made to winIDEA with the given workspace.
        """
        if workspaceFileName != None:
            self.connect(workspaceFileName)

        
    def connect(self, workspaceFileName = ''):
        """
        Connects to winIDEA and loads the given workspace. If no
        workspace file is specified, the most recently used workspace
        is opened.
        """
        if self.__connectionMgr == None:
            self.__connectionMgr = isystem.connect.ConnectionMgr()
            self.__connectionMgr.connectMRU(workspaceFileName)
        else:
            raise Exception("This instance of ICFactory is already connected!" +
                            " Create another instance to make another connection!")

    def connectWithId(self, id):
        """
        Connects to winIDEA, which was started with the specified id (command line
        option /id:<idString>). If such instance of winIDEA is not found, an
        exception is raised.
        """
        self.__connectionMgr = isystem.connect.ConnectionMgr()
        connectionConfig = isystem.connect.CConnectionConfig()
        connectionConfig.instanceId(id)
        port = 0
        port = self.__connectionMgr.findExistingInstance('', connectionConfig)
        if port < 0:
            raise Exception("winIDEA with id == '" + str(id) + "' not found!")
        self.__connectionMgr.connect('', port)

        
    def getDebugFacade(self):
        """ Returns instance of CDebugFacade. """
        if self.__debugCtrl == None:
            self.__debugCtrl = isystem.connect.CDebugFacade(self.__connectionMgr)

        return self.__debugCtrl


    def getDataCtrl(self):
        """ Returns instance of CDataController. """
        if self.__dataCtrl == None:
            self.__dataCtrl = isystem.connect.CDataController(self.__connectionMgr)

        return self.__dataCtrl

        
    def getProjectCtrl(self):
        """ Returns instance of CProjectController. """
        if self.__projectCtrl == None:
            self.__projectCtrl = isystem.connect.CProjectController(self.__connectionMgr)

        return self.__projectCtrl


    def getDocumentCtrl(self, fileName, openMode):
        """ Returns instance of CDocumentController.

            Parameters:
              isNew    - set it to true, if new document should be opened
              fileName - name of the new document
        """
        __documentCtrl = isystem.connect.CDocumentController(self.__connectionMgr, fileName, openMode)
        return __documentCtrl


    def getAnalyzerDocCtrl(self, docType, fileName, openMode):
        """ Returns instance of CAnalyzerController.

            Parameters:
              isNew    - set it to true, if new document should be opened
              fileName - name of the new document
        """
        __analyzerDocCtrl = isystem.connect.CAnalyzerDocController(self.__connectionMgr,
                                                                   docType, fileName, openMode)
        return __analyzerDocCtrl


    def getTerminalDocCtrl(self):
        """ Returns instance of CTerminalController."""
        if self.__terminalDocCtrl == None:
            self.__terminalDocCtrl = isystem.connect.CTerminalDocController(self.__connectionMgr)

        return self.__terminalDocCtrl


    def getHILCtrl(self):
        """ Returns instance of CHILController."""
        if self.__hilCtrl == None:
            self.__hilCtrl = isystem.connect.CHILController(self.__connectionMgr)
        return self.__hilCtrl


    def getIdeCtrl(self):
        """ Returns instance of CIDEController."""
        if self.__ideCtrl == None:
            self.__ideCtrl = isystem.connect.CIDEController(self.__connectionMgr)
        return self.__ideCtrl


    def getWorkspaceCtrl(self):
        """ Returns instance of CWorkspaceController."""
        if self.__workspaceCtrl == None:
            self.__workspaceCtrl = isystem.connect.CWorkspaceController(self.__connectionMgr)

        return self.__workspaceCtrl


    def getProfilerCtrl(self):
        """ Returns instance of CProfilerController."""
        if self.__profilerCtrl == None:
            self.__profilerCtrl = isystem.connect.CProfilerController(self.__connectionMgr)
        return self.__profilerCtrl


    def getTestCaseCtrl(self, functionName, retValName):
        """
        Returns instance of CTestCaseController. It is caller's responsibility to
        call clean() and destroy() on returned object when it is no longer needed.
        Example:

            icFactory = isystem.icutils.getFactory()
            testCtrl = icFactory.getTestCaseCtrl("funcTestInt2", "retVal")
            testCtrl.createParameter(0, "a")
            testCtrl.createParameter(1, "b")
            testCtrl.createParameter(2, "c")
            testCtrl.init()
            testCtrl.modify("a", "11")
            testCtrl.modify("b", "21")
            testCtrl.modify("c", "31")

            testCtrl.run()
            testCtrl.waitUntilStopped()

            result = testCtrl.s2i64(testCtrl.evaluate("retVal == 64")) 
            if result == 1:
                print "OK"
            else:
                print "Error: result = ", result

            # It is very important that we destroy the test case after usage!
            testCtrl.clean()
            testCtrl.destroy()
        
        """
        self.__testCaseCtrl = isystem.connect.CTestCaseController(self.__connectionMgr,
                                                                  functionName,
                                                                  retValName)
        return self.__testCaseCtrl


    def getCoverageCtrl(self, fileName, openMode):
        """ Returns instance of CoverageController.

            Parameters:
              fileName - name of the new document
              openMode - 'r' opens existing file, 'w' opens
                         existing file and deletes contents or creates new file,
                         'a' opens existing file and keeps contents or creates 
                         new file.
        """
        __coverageCtrl = isystem.connect.CCoverageController(self.__connectionMgr, fileName, openMode)
        return __coverageCtrl


    def getConnectionMgr(self):
        """
        Returns connection manager. Use this method, when you need the
        connection manager to instantiate 'isystem.connect' classes
        directly.
        """
        return self.__connectionMgr

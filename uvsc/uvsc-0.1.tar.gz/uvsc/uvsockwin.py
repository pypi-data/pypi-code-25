from ctypes import *
from enum import Enum
import platform
import os

class UVSC_STATUS (Enum):
	UVSC_STATUS_SUCCESS = 0
	UVSC_STATUS_FAILED = 1
	UVSC_STATUS_NOT_SUPPORTED = 2
	UVSC_STATUS_NOT_INIT = 3
	UVSC_STATUS_TIMEOUT = 4
	UVSC_STATUS_INVALID_CONTEXT = 5
	UVSC_STATUS_INVALID_PARAM = 6
	UVSC_STATUS_BUFFER_TOO_SMALL = 7
	UVSC_STATUS_CALLBACK_IN_USE = 8
	UVSC_STATUS_COMMAND_ERROR = 9

class UVSC_VTT_TYPE (Enum):
	VTT_void = 0 
	VTT_bit = 1 
	VTT_char = 2 
	VTT_uchar = 3 
	VTT_int = 4 
	VTT_uint = 5 
	VTT_short = 6 
	VTT_ushort = 7 
	VTT_long = 8 
	VTT_ulong = 9 
	VTT_float = 10 
	VTT_double = 11 
	VTT_ptr = 12 
	VTT_union = 13 
	VTT_struct = 14 
	VTT_func = 15 
	VTT_string = 16 
	VTT_enum = 17 
	VTT_field = 18 
	VTT_int64 = 19 
	VTT_uint64 = 20 


class UVSC_RUNMODE (Enum):
	UVSC_RUNMODE_NORMAL = 0
	UVSC_RUNMODE_LABVIEW = 1
	UVSC_RUNMODE_END = 2

class UVSC_PBAR (Enum):	
	UVSC_PBAR_INIT = 0
	UVSC_PBAR_TEXT = 1
	UVSC_PBAR_POS = 2
	UVSC_PBAR_STOP = 3

class UVSC_CB_TYPE (Enum):
	UVSC_CB_ERROR = 0
	UVSC_CB_ASYNC_MSG = 1
	UVSC_CB_DISCONNECTED = 2
	UVSC_CB_BUILD_OUTPUT_MSG = 3
	UVSC_CB_PROGRESS_BAR_MSG = 4
	UVSC_CB_CMD_OUTPUT_MSG = 5 
	
class UVSC_BKTYPE (Enum): 
	BRKTYPE_EXEC = 1 
	BRKTYPE_READ = 2 
	BRKTYPE_WRITE = 3 
	BRKTYPE_READWRITE = 4 
	BRKTYPE_COMPLEX = 5 


MIN_AUTO_PORT_NUMBER = 5101
MAX_AUTO_PORT_NUMBER = 5110

class UVSOCK_CMD (LittleEndianStructure):
	_fields_ = [("m_nTotalLen", c_uint), ("m_eCmd", c_uint), ("m_nBufLen", c_uint),
				("cycles", c_ulonglong), ("tStamp", c_double),("m_Id", c_uint),
				("data", c_char_p)]

CMD_MAX_BUFFER = 2048

class UVSC_EXECCMD (LittleEndianStructure):
	_fields_ = [("bEcho", c_uint32),
				("nRes",c_uint32 * 7), 
				("len", c_uint32), ("sCmd", c_char * CMD_MAX_BUFFER)]

class UVSC_VSET (LittleEndianStructure):
	_fields_ = [("tval_Type", c_uint32), ("tval_v1", c_uint32), ("tval_v2", c_uint32), ("nLen", c_uint32), ("str", c_char * 256)]

FILENAME_MAX_BUFFER = 2048

class UVSC_PRJDATA (LittleEndianStructure):
	_fields_= [("nLen", c_uint32),("nCode", c_uint32), ("szNames", c_char * FILENAME_MAX_BUFFER)]

MEM_MAX_BUFFER = 1*1024

class UVSC_AMEM (LittleEndianStructure):
	_fields_= [("nAddr", c_uint64), ("nBytes", c_uint32), ("ErrAddr", c_uint64), ("nErr", c_uint32), ("aBytes", c_ubyte * MEM_MAX_BUFFER)]

class UVSC_BKPARM (LittleEndianStructure):
	_fields_= [("type", c_uint32), ("count", c_uint32), ("accSize", c_uint32), ("nExpLen", c_uint32), ("nCmdLen", c_uint32), ("szBuffer", c_char*1024)]

class UVSC_BKRSP (LittleEndianStructure):
	_fields_= [("type", c_uint32), ("count", c_uint32), ("enabled", c_uint32), ("nTickMark", c_uint32), ("nAddress", c_uint64), ("nExpLen", c_uint32), ("szBuffer", c_char*512)]


debug_on = 0

def debugprint (*message):
	if (debug_on == 1):
		print (message)
		

def Init ():
	"""
	The Init method needs to be called before any other function of pyUVSC 
	can be used.
	"""	
	global uvscdll
	debugprint ("System Architecture detected: " + platform.architecture()[0] + " " + platform.architecture()[1])
	if (platform.architecture()[0] == "64bit") :
		debugprint ("Loading uvsc64.dll")
		path = os.path.dirname(__file__)
		uvscdll = CDLL(path + "/UVSC64.dll")
	else:
		debugprint ("Windows 32-bit not supported")
	debugprint ("DLL handle" , uvscdll)
	min_port = c_uint(MIN_AUTO_PORT_NUMBER)
	max_port = c_uint(MAX_AUTO_PORT_NUMBER)
	result = uvscdll.UVSC_Init(min_port, max_port)    
	debugprint (UVSC_STATUS(result).name)
	
def UnInit ():
	"""
	The UnInit method needs to be called to clean up pyUVSC after usage.
	"""	
	debugprint ("UVSC_UnInit")
	result = uvscdll.UVSC_UnInit()    
	debugprint (UVSC_STATUS(result).name)
	
def Version ():
	"""
	Returns the version of the remote UVSocket instance
	"""
	debugprint ("UVSC_Version")
	pUVSCVersion = c_uint()
	pUVSOCKVersion = c_uint()
	uvscdll.UVSC_Version(byref(pUVSCVersion), byref(pUVSOCKVersion))    
	return (pUVSOCKVersion.value)   


UVSC_CALLBACK = CFUNCTYPE(None,POINTER(c_uint),c_uint,UVSOCK_CMD)
@UVSC_CALLBACK
def uvsc_cb(custom, type, uvsock_cmd):
	debugprint ("CALLBACK")
	debugprint (UVSC_CB_TYPE(type).name)
	debugprint (uvsock_cmd)
	debugprint (uvsock_cmd.m_nBufLen)


def OpenConnection (Port):
	"""
	Open the Connection to a running instance of uVision. 
	
	:param Port: Port number of remote uVision IDE instance. 
	:type Port: Integer 
	"""	
	debugprint ("UVSC_OpenConnection")
	global iConnHandle
	iConnHandle = c_uint()	
	name = c_char_p()
	pPort = c_int(Port)
	uvCmd = c_char_p()
	uvRunmode = c_uint()
	result = uvscdll.UVSC_OpenConnection(None, byref(iConnHandle), byref(pPort), None, None, uvsc_cb, None, None, None, None)
	debugprint ("handle = " + str(iConnHandle))
	debugprint (UVSC_STATUS(result).name)

def CloseConnection ():
	"""
	Close an open Connection. 
	"""	
	debugprint ("UVSC_CloseConnection")
	result = uvscdll.UVSC_CloseConnection(None, 1)    
	debugprint (UVSC_STATUS(result).name)
	
def GEN_SHOW ():
	"""
	Show the IDE GUI.
	"""	
	debugprint ("UVSC_GEN_SHOW")
	result = uvscdll.UVSC_GEN_SHOW(None)    
	debugprint (UVSC_STATUS(result).name)

def GEN_HIDE ():
	"""
	Hide the IDE GUI.
	"""		
	debugprint ("UVSC_GEN_HIDE")
	result = uvscdll.UVSC_GEN_HIDE(None)    
	debugprint (UVSC_STATUS(result).name)    


#
#  Project Management
#

def PRJ_LOAD (filename):
	"""
	Load a uVision project. Will unload an open project or workspace of the 
	connected instance first.
		
	:param filename: Absolute path and file name of project to load. 
	:type filename: str 
	"""	
	debugprint ("UVSC_PRJ_LOAD")
	if (len(filename) > FILENAME_MAX_BUFFER):
		print ("Warning: file name too long")
	prj_data = UVSC_PRJDATA()
	prj_data.nLen = FILENAME_MAX_BUFFER
	prj_data.nCode = 0
	prj_data.szNames = bytes(filename, 'utf-8')
	result = uvscdll.UVSC_PRJ_LOAD(iConnHandle, prj_data, FILENAME_MAX_BUFFER)    
	debugprint (UVSC_STATUS(result).name)


def PRJ_CLOSE ():
	"""
	Unoad a uVision project of the connected IDE instance.
	"""	
	debugprint ("UVSC_PRJ_CLOSE")
	result = uvscdll.UVSC_PRJ_CLOSE(iConnHandle)    
	debugprint (UVSC_STATUS(result).name)
	

def PRJ_ADD_FILE (groupname, filename):
	"""
	*Not implemented.* 
	"""	
	debugprint ("UVSC_PRJ_ADD_FILE")
	name = groupname + '\x00' + filename
	if (len(name) > FILENAME_MAX_BUFFER):
		debugprint ("file name string too long")
	prj_data = UVSC_PRJDATA()
	prj_data.nLen = FILENAME_MAX_BUFFER
	prj_data.nCode = 0
	prj_data.szNames =  bytes(name, 'utf-8')
	result = uvscdll.UVSC_PRJ_ADD_FILE(iConnHandle, prj_data, FILENAME_MAX_BUFFER)    
	debugprint (UVSC_STATUS(result).name)


def PRJ_DEL_FILE (groupname, filename):
	"""
	*Not implemented.* 
	"""	
	debugprint ("UVSC_PRJ_DEL_FILE")
	if (len(filename) > FILENAME_MAX_BUFFER):
		debugprint ("file name string too long")
	prj_data = UVSC_PRJDATA()
	prj_data.nLen = FILENAME_MAX_BUFFER
	prj_data.nCode = 0
	prj_data.szNames =  bytes(groupname, 'utf-8')
	result = uvscdll.UVSC_PRJ_DEL_FILE(iConnHandle, prj_data, FILENAME_MAX_BUFFER)    
	debugprint (UVSC_STATUS(result).name)

def PRJ_ENUM_FILES ():
	"""
	*Not implemented.* 
	"""	
	debugprint("not implemented")

def PRJ_ADD_GROUP ():
	"""
	*Not implemented.* 
	"""	
	debugprint("not implemented")

def PRJ_DEL_GROUP ():
	"""
	*Not implemented.* 
	"""	
	debugprint("not implemented")

def PRJ_SET_TARGET ():
	"""
	*Not implemented.* 
	"""
	debugprint("not implemented")	

def PRJ_SET_OUTPUTNAME ():
	"""
	*Not implemented.* 
	"""	
	debugprint("not implemented")

def PRJ_ENUM_GROUPS ():
	"""
	*Not implemented.* 
	"""	
	debugprint("not implemented")

def PRJ_ENUM_TARGETS ():
	"""
	*Not implemented.* 
	"""
	debugprint("not implemented")	

def PRJ_ACTIVE_FILES ():
	"""
	*Not implemented.* 
	"""
	debugprint("not implemented")	

def PRJ_BUILD ():
	"""
	Start Build of currently loaded project and target. 
	"""	
	debugprint ("UVSC_PRJ_BUILD")
	result = uvscdll.UVSC_PRJ_BUILD(iConnHandle, 1)    
	debugprint (UVSC_STATUS(result).name)

def PRJ_BUILD_CANCEL ():
	"""
	*Not implemented.* 
	"""	
	debugprint("not implemented")

def PRJ_CLEAN ():
	"""
	*Not implemented.* 
	"""	
	debugprint("not implemented")

def PRJ_FLASH_DOWNLOAD ():
	"""
	*Not implemented.* 
	"""	
	debugprint ("PRJ_FLASH_DOWNLOAD")
	result = uvscdll.PRJ_FLASH_DOWNLOAD(iConnHandle, 1)    
	debugprint (UVSC_STATUS(result).name)
	debugprint("not implemented")

def PRJ_GET_OPTITEM ():
	"""
	*Not implemented.* 
	"""	
	debugprint("not implemented")

def PRJ_SET_OPTITEM ():
	"""
	*Not implemented.* 
	"""	
	debugprint("not implemented")

def PRJ_GET_DEBUG_TARGET ():
	"""
	*Not implemented.* 
	"""	
	debugprint("not implemented")

def PRJ_SET_DEBUG_TARGET ():
	"""
	*Not implemented.* 
	"""	
	debugprint("not implemented")

def PRJ_CMD_PROGRESS ():
	"""
	*Not implemented.* 
	"""		
	debugprint("not implemented")

def PRJ_GET_OUTPUTNAME ():
	"""
	*Not implemented.* 
	"""		
	debugprint("not implemented")

def PRJ_GET_CUR_TARGET ():
	"""
	*Not implemented.* 
	"""		
	debugprint("not implemented")

#
#  Debugging 
#

def DBG_ENTER ():
	"""
	Enter debug session. 
	"""	
	debugprint ("UVSC_DBG_ENTER")
	result = uvscdll.UVSC_DBG_ENTER(iConnHandle)    
	debugprint (UVSC_STATUS(result).name)

def DBG_EXIT ():
	"""
	Leave debug session. 
	"""	
	debugprint ("UVSC_DBG_EXIT")
	result = uvscdll.UVSC_DBG_EXIT(iConnHandle)    
	debugprint (UVSC_STATUS(result).name)

def DBG_START_EXECUTION ():
	"""
	Start execution in debugger. 
	"""	
	debugprint ("UVSC_START_EXECUTION ")
	status = c_int()
	status = uvscdll.UVSC_DBG_START_EXECUTION (iConnHandle, byref(status))    
	debugprint ("status = " + str(status))
	debugprint (UVSC_STATUS(status).name)

def DBG_RUN_TO_ADDRESS ():
	"""
	*Not implemented.* 
	"""	
	debugprint("not implemented")

def DBG_STOP_EXECUTION ():
	"""
	Stop exection in debugger. 
	"""	
	debugprint ("UVSC_START_EXECUTION ")
	status = c_int()
	status = uvscdll.UVSC_DBG_STOP_EXECUTION (iConnHandle, byref(status))    
	debugprint ("status = " + str(status))
	debugprint (UVSC_STATUS(status).name)

def DBG_STATUS ():
	"""
	*Not implemented.* 
	"""	
	debugprint ("UVSC_STATUS ")
	status = c_int()
	result = uvscdll.UVSC_DBG_STATUS (iConnHandle, byref(status))    
	debugprint ("status = " + str(status))
	debugprint (UVSC_STATUS(result).name)
	return UVSC_STATUS(status.value).name

def DBG_STEP_HLL ():
	"""
	Execute a single high-level source step. 
	"""	
	debugprint ("UVSC_DBG_STEP_HLL")
	result = uvscdll.UVSC_DBG_STEP_HLL(iConnHandle)    
	debugprint (UVSC_STATUS(result).name)

def DBG_STEP_HLL_N (count):
	"""
	Execute a number of high-level source steps.
	
	:param count: Number of steps
	:param type: Integer 
	"""	

	debugprint ("UVSC_DBG_STEP_HLL_N")
	for i in range(1, count):
		DBG_STEP_HLL()

def DBG_STEP_INSTRUCTION ():
	"""
	Execute an instruction-level step. 
	"""	
	debugprint ("UVSC_DBG_STEP_INSTRUCTION")
	result = uvscdll.UVSC_DBG_STEP_INSTRUCTION(iConnHandle)    
	debugprint (UVSC_STATUS(result).name)

def DBG_STEP_INSTRUCTION_N (count):
	"""
	Execute a number of instruction-level steps.
	
	:param count: Number of steps
	:param type: Integer 
	"""	
	debugprint ("UVSC_DBG_STEP_INSTRUCTION_N")
	for i in range(1, count):
		DBG_STEP_INSTRUCTION()

def DBG_STEP_INTO ():
	"""
	*Not implemented.* 
	"""	
	debugprint ("UVSC_DBG_STEP_INTO")
	result = uvscdll.UVSC_DBG_STEP_INTO(iConnHandle)    
	debugprint (UVSC_STATUS(result).name)

def DBG_STEP_INTO_N (count):
	"""
	*Not implemented.* 
	"""
	debugprint ("UVSC_DBG_STEP_INTO_N")
	for i in range(1, count):
		DBG_STEP_INTO()

def DBG_STEP_OUT ():
	"""
	*Not implemented.* 
	"""
	debugprint ("UVSC_DBG_STEP_OUT")
	result = uvscdll.UVSC_DBG_STEP_OUT(iConnHandle)    
	debugprint (UVSC_STATUS(result).name)

def DBG_RESET ():
	"""
	*Not implemented.* 
	"""
	debugprint ("UVSC_DBG_RESET")
	result = uvscdll.UVSC_DBG_RESET(iConnHandle)    
	debugprint (UVSC_STATUS(result).name)

#class UVSC_AMEM (LittleEndianStructure):
#	_fields_= [("nAddr", c_uint64), ("nBytes", c_uint32), ("ErrAddr", c_uint64), ("nErr", c_uint32), ("aBytes", c_byte * MEM_MAX_BUFFER)]

def DBG_MEM_READ (addr, size):
	"""
	Read a block of memory. Maximum size is defined in MEM_MAX_BUFFER.
	
	:param addr: First Address of memory block to read.
	:param size: Size of memory block in bytes.
	:returns: bytearray 
	"""
	if (size > MEM_MAX_BUFFER):
		size = MEM_MAX_BUFFER
		print("Warning: size parameter truncated")
	amem = UVSC_AMEM()
	amem.nAddr = c_uint64(addr)
	amem.nBytes = c_uint32(size)	
	result = uvscdll.UVSC_DBG_MEM_READ(iConnHandle, byref(amem), amem.nBytes+24)
	debugprint (UVSC_STATUS(result).name)	
	return (bytearray(amem.aBytes))
	

def DBG_MEM_WRITE (addr, size, buf):
	"""
	Write a block of memory. Maximum size is defined in MEM_MAX_BUFFER.
	
	:param addr: First Address of memory block to write.
	:param size: Size of memory block in bytes.
	:param buf: Buffer to write as bytearray
	"""	
	if (size > MEM_MAX_BUFFER):
		size = MEM_MAX_BUFFER
		print("Warning: size parameter truncated")
	amem = UVSC_AMEM()
	amem.nAddr = c_uint64(addr)
	amem.nBytes = c_uint32(size)
	for i in range(1, size):
		amem.aBytes[i] = c_ubyte(buf[i]) 	
	result = uvscdll.UVSC_DBG_MEM_WRITE(iConnHandle, byref(amem), amem.nBytes+24)
	debugprint (UVSC_STATUS(result).name)	

#class UVSC_BKPARM (LittleEndianStructure):
#	_fields_= [("type", c_uint32), ("count", c_uint32),("accSize", c_uint32),("nExpLen", c_uint32),("nCmdLen", c_uint32), ("szBuffer". c_char*1024)]

def DBG_CREATE_BP (type, expr, count):
	"""
	*Not implemented.* 
	"""	
	bkparm = UVSC_BKPARM()
	bkparm.type =  c_uint32(UVSC_BKTYPE[type].value)
	bkparm.count = c_uint32(count)
	bkparm.nExpLen = len(expr) + 1
	bkrsp = UVSC_BKRSP()
	bkptrsplen = c_uint32()
	result = uvscdll.UVSC_DBG_CREATE_BP(iConnHandle, byref(bkparm), bkparm.nExpLen + 32, byref(bkrsp), byref(bkptrsplen))
	debugprint (UVSC_STATUS(result).name)	

def DBG_CHANGE_BP ():
	"""
	*Not implemented.* 
	"""
	debugprint("not implemented")

def DBG_ENUMERATE_BP ():
	"""
	*Not implemented.* 
	"""
	debugprint("not implemented")

def DBG_SERIAL_GET ():
	"""
	*Not implemented.* 
	"""
	debugprint("not implemented")

def DBG_SERIAL_PUT ():
	"""
	*Not implemented.* 
	"""
	debugprint("not implemented")

def DBG_ITM_REGISTER ():
	"""
	*Not implemented.* 
	"""
	debugprint("not implemented")

def DBG_ITM_UNREGISTER ():
	"""
	*Not implemented.* 
	"""
	debugprint("not implemented")

def DBG_CALC_EXPRESSION (expr):
	"""
	Calculate the value of an expression. This can be used to get any value
	or variable from the debugger.
	
	:param expr: Expression to evaluate.
	:param type: String
	:return: Result as integer
	"""
	uvsc_vset = UVSC_VSET()
	uvsc_vset.tval_Type = c_uint32(0)
	uvsc_vset.nLen = len(expr) + 1
	uvsc_vset.str =  bytes(expr, 'utf-8')  	
	result = uvscdll.UVSC_DBG_CALC_EXPRESSION(iConnHandle, byref(uvsc_vset), uvsc_vset.nLen + 16)
	debugprint ("val1= ", uvsc_vset.tval_v1, "val2= ",uvsc_vset.tval_v2)    
	debugprint (UVSC_VTT_TYPE(uvsc_vset.tval_Type).name)
	debugprint (UVSC_STATUS(result).name)
	return uvsc_vset.tval_v1

def DBG_EVAL_WATCH_EXPRESSION ():
	"""
	*Not implemented.* 
	"""
	debugprint("not implemented")

def DBG_REMOVE_WATCH_EXPRESSION ():
	"""
	*Not implemented.* 
	"""
	debugprint("not implemented")

def DBG_ENUM_VARIABLES ():
	"""
	*Not implemented.* 
	"""
	debugprint("not implemented")

def DBG_VARIABLE_SET ():
	"""
	*Not implemented.* 
	"""
	debugprint("not implemented")

def DBG_ENUM_VTR ():
	"""
	*Not implemented.* 
	"""
	debugprint("not implemented")

def DBG_VTR_GET (name):
	"""
	Return the value of a Virtual Register (VTREG)
	
	:param name: Name of VRTEG.
	:param type: String 
	:return: Value as Integer
	"""
	uvsc_vset = UVSC_VSET()
	uvsc_vset.tval_Type = c_uint32(0)
	uvsc_vset.nLen = len(name) + 1
	uvsc_vset.str = name  
	result = uvscdll.UVSC_DBG_VTR_GET(iConnHandle, byref(uvsc_vset), uvsc_vset.nLen + 16)
	debugprint (uvsc_vset.tval_v1, uvsc_vset.tval_v2)    
	debugprint (UVSC_VTT_TYPE(uvsc_vset.tval_Type).name)
	debugprint (UVSC_STATUS(result).name)
	return(uvsc_vset.tval_v1)


def DBG_VTR_SET ():
	"""
	*Not implemented.* 
	"""
	debugprint("not implemented")

def DBG_ENUM_STACK ():
	"""
	*Not implemented.* 
	"""
	debugprint("not implemented")

def DBG_ENUM_TASKS ():
	"""
	*Not implemented.* 
	"""
	debugprint("not implemented")

def DBG_ENUM_MENUS ():
	"""
	*Not implemented.* 
	"""
	debugprint("not implemented")

def DBG_MENU_EXEC ():
	"""
	*Not implemented.* 
	"""
	debugprint("not implemented")

def DBG_ADR_TOFILELINE ():
	"""
	*Not implemented.* 
	"""
	debugprint("not implemented")

def DBG_ADR_SHOWCODE ():
	"""
	*Not implemented.* 
	"""
	debugprint("not implemented")

def DBG_WAKE ():
	"""
	*Not implemented.* 
	"""
	debugprint("not implemented")
 
def DBG_SLEEP ():
	"""
	*Not implemented.* 
	"""
	debugprint("not implemented")

#class UVSC_EXECCMD (Structure):
#	_fields_ = [("bEcho", c_uint32),
#				("nRes",c_uint32 * 7), 
#				("len", c_uint32), ("sCmd", c_char * CMD_MAX_BUFFER)]
 
def DBG_EXEC_CMD (cmd):
	"""
	Execute a debugger command.
	
	:param cmd: Full command
	:param type: String 
	"""
	if (len(cmd) > CMD_MAX_BUFFER):
		print("Warning: command string truncated")
	cmd_data = UVSC_EXECCMD()
	cmd_data.bEcho = 0;
	cmd_data.len = len(cmd)+1
	cmd_data.sCmd = bytes(cmd, 'utf-8')
	result = uvscdll.UVSC_DBG_EXEC_CMD(iConnHandle, cmd_data, CMD_MAX_BUFFER + 36)    
	debugprint (UVSC_STATUS(result).name)



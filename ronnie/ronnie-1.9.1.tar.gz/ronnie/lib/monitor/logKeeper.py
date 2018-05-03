#############################################################################################
#Project roNNie
#Simple Framework for AI Development
#############################################################################################
# Created by   : Kevin Lok
# Created Date : 20180316
# LICENSE 	   : MIT
# Version      : 1.9.x
# Summary      : To handle logging 
#############################################################################################
import os
import sys
import json
import logging
import logging.config

import ronnie.meta as meta
import ronnie.lib.util as util

logger = logging.getLogger("roNNie")

#such cofiguration used to save the log to files

def initial(projPath, modelName, type="proj", logLevel=logging.INFO):
	
	logging.info("Project Path {0}".format(projPath))

	if type == meta.SYS:
		logging.basicConfig(level=logLevel)
		
	else:
		modelsLogsPath 		= os.path.realpath(projPath + "/models/" + modelName + "//logs//")
		modelsCfgPath 	= os.path.realpath(projPath + "/models/" + modelName + "//conf//")
		
		
		if not os.path.exists(modelsCfgPath):
			os.makedirs(modelsCfgPath)
			logging.info("Path : {0}".format(modelsCfgPath))
		if not os.path.exists(modelsLogsPath):
			os.makedirs(modelsLogsPath)
			logging.info("Path : {0}".format(modelsLogsPath))
		
		defaultLogDictPath = projPath + "/conf/"
		
		logDictFile = "/logConf.json"
		tensorLogFile = "/tensorflow.log"
	
		defaultCfgFilePath = os.path.realpath(defaultLogDictPath + logDictFile)
		
		tensorLogPath = os.path.realpath(modelsLogsPath + tensorLogFile)
		
		modelsCfgFile = os.path.realpath(modelsCfgPath + logDictFile)
		
		if not os.path.exists(modelsCfgFile):
			logging.info("{0} not exist ".format(modelsCfgFile) )
			if os.path.exists(defaultCfgFilePath):
				with open(defaultCfgFilePath, 'rt') as f:
					config = json.load(f)
					jObjHandlers = config["handlers"]
					
					fName_debug = jObjHandlers["debug_file_handler"]["filename"]
					fName_info  = jObjHandlers["info_file_handler"]["filename"]
					fName_error = jObjHandlers["error_file_handler"]["filename"]
					
					debug_logsFilePath = os.path.realpath(modelsLogsPath + fName_debug)
					info_logsFilePath = os.path.realpath(modelsLogsPath + fName_info)
					error_logsFilePath = os.path.realpath(modelsLogsPath + fName_error)
					
					jObjHandlers["debug_file_handler"]["filename"] = debug_logsFilePath
					jObjHandlers["info_file_handler"]["filename"]  = info_logsFilePath
					jObjHandlers["error_file_handler"]["filename"] = error_logsFilePath
					
					config["handlers"] = jObjHandlers

					with open(modelsCfgFile, 'wt') as cfgFile:
						json.dump(config, cfgFile)
			else:
				logging.basicConfig(level=logLevel)
				logging.error("Can't Read config file, use BasicConfig")
		
		logging.info("{0} exist ".format(modelsCfgFile) )
		with open(modelsCfgFile, 'rt') as f:
			config = json.load(f)		
			logging.config.dictConfig(config)
			rLog = logging.getLogger("roNNie")
			rLog.setLevel(logLevel)
			logging.info("Initial DictConf for LK done.")
				
		try:
			tLog = logging.getLogger('tensorflow')
			tLog.setLevel(logLevel)
			formatter = logging.Formatter('%(message)s')
			fh = logging.FileHandler(tensorLogPath)
			fh.setLevel(logLevel)
			fh.setFormatter(formatter)
			tLog.addHandler(fh)
			
		except IOError as iE:
			logger.error("File IO Error")
		except:
			logger.error("INITIAL - Unexpected error: {}".format(sys.exc_info()[0]))
				
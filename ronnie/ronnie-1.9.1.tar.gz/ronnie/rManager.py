#############################################################################################
#Project roNNie
#Simple Framework for AI Development
#############################################################################################
# Created by   : Kevin Lok
# Created Date : 20180316
# LICENSE 	   : MIT
# Version      : 1.9.x
# Summary	   : To create deep learning CNN project through ronnie AI framework for starter

import sys
import os
import shutil
import logging
import zipfile

import ronnie.lib.monitor.logKeeper 	as lk
import ronnie.meta			as meta

lk.initial("","",type=meta.SYS)
logger = logging.getLogger("roNNie")
__version__= '1.9.1'

def version():
	print("Project roNNie version : {0}. ".format(__version__))

def main():
	path = os.path.abspath(__file__)
	dir_path = os.path.dirname(path)
	#print("execution path {0}, {1}".format(path, dir_path))
	
	packageFullPathWithName = sys.modules['ronnie']
	realPackagePath = os.path.realpath(os.path.dirname(sys.modules['ronnie'].__file__))
	
	#print("packageFullPathWithName {0}".format(packageFullPathWithName))
	#print("realPackagePath {0}".format(realPackagePath))
	
	#print("sys.argv {0}".format(sys.argv))
	if not (len(sys.argv) < 2 ):
		script = sys.argv[0]
		action = sys.argv[1]
		if action == "--version":
			version()
		elif action == "--project":
			if not (len(sys.argv) < 4 ):
			
				projectName = sys.argv[2]
				projectPath = os.path.realpath(sys.argv[3]+"./" + projectName)
				
				#tDrive, tPath = os.path.splitdrive(projectPath)	

#Better create a Project ini to store project, project path information				
				if not projectName is None:
						if not (os.path.exists(projectPath)):
							#os.makedirs(projectPath)
							print(" [CREATing] : Project : {0} at {1}.".format(projectName,  projectPath))
							print(" [BUILDing] : Project Structure...")
							os.makedirs(projectPath + "/designer")
							os.makedirs(projectPath + "/logs")
							print(" [SYNCing]  : Necessary files ...")
							
							srcCfPath = os.path.realpath(realPackagePath+"/conf")
							desCfPath = os.path.realpath(projectPath + "/conf")
							shutil.copytree(srcCfPath,desCfPath )
							
							dataPath = projectPath + "/data/digitalRec"
							srcDataPath = os.path.realpath(realPackagePath+"/data")
							desDataPath = os.path.realpath(projectPath + "/data")
							shutil.copytree(srcDataPath,desDataPath)
							
							print(" [UNPACKing] : Project Data...")
							zip_ref = zipfile.ZipFile(os.path.realpath(dataPath + "/train.zip"), 'r')
							zip_ref.extractall(dataPath)
							zip_ref = zipfile.ZipFile(os.path.realpath(dataPath + "/test.zip"), 'r')
							zip_ref.extractall(dataPath)
							zip_ref.close()
							
							print(" [Creating] : digitalr...")
							srcDrPath = os.path.realpath(realPackagePath +"/examples/digitalr.py")
							desDrPath = os.path.realpath(projectPath + "/digitalr.py")
							shutil.copy2(srcDrPath, desDrPath)
							
							#print(" [Creating] : cifar...")
							#shutil.copy2(realPackagePath +"./examples/cifar.py", projectPath + "/cifar.py")
							print(" [DONE]     : Project : {0} was successfully created at {1}.".format(projectName,  projectPath))
							
							print("Next Step: rManager --template to list the Model Templates")
							# cnn, rnn, .....
							# {Number of Convolution Layer}c{Number of Pool Layer}p{Number of Dense Layer}
							#  example : 2c2p2d
						#Read and Print realPackagePath +"/template/cnn.template"
							#shutil.copy2(realPackagePath + '/template/cnn/xxxxx.py', projectPath + '/designer/xxxx.py')
							#add instruction to next step
						else:
							logger.error("Project Path was already created. Please choose new project path.")
				
				#identify the model type and copy the template to the designer folder
				
			else:
				logger.error("ERROR: Missing project name, projectPath.")
				#render('%(BG_YELLOW)s%(RED)s%(BOLD)sHey this is a test%(NORMAL)s')
				print("--project {ProjectName} {ProjectPath} to create the AI project")
		elif action == "--template":
			print("Template list: {NumberOf}(c)onvolution{NumberOf}(p)ool{NumberOf}(d)ense Layer")
			print("Example c1p1d1 in terms of : 1 (c)onvolution + 1(p)ool + 1 (d)ense Layer")
			print("##########################################################################")
			templateListFullPath = realPackagePath+ "/template/cnn.template"

			with open(templateListFullPath,'r', encoding='UTF-8') as f:
				lines = f.read()
				f.close()
				print("Total 17 cnn Templates: {0}".format(lines))
				
			if not len(sys.argv) < 5:
				modelName = sys.argv[2]
				templateName = sys.argv[3]
				projectPath =  sys.argv[4]
				templateFullPath = realPackagePath+ "/template/cnn/" + templateName +".py"
				if os.path.exists(templateFullPath) and os.path.exists(projectPath):
					logger.debug(os.path.exists(projectPath))
					logger.debug(os.path.exists(templateFullPath))
					shutil.copy2(os.path.realpath(templateFullPath), os.path.realpath(projectPath + "/designer/" +templateName+ ".py"))
					
					print("Template saved at {0}".format(os.path.realpath(projectPath+ "/designer/")))
				else:
					if not os.path.exists(projectPath):
						logger.error("Project Path {0} INCORRECT.".format(projectPath))
					else:
						logger.error("No Template named : {0}".format(templateName))
					
			else:
				print("--template cnn {TemplateName} {ProjectPath}")
		elif action == "--help":
			print("--version : show the exist version")
			print("--project {ProjectName} {ProjectPath} : Create the AI project")
			print("--template")
		else:
			print("--help : show the options")
			
	else:
		version()
		print("Questions: ronnie --help")

if __name__ == "__main__":
 # if you call this script from the command line (the shell) it will
 # run the 'main' function
	main()	
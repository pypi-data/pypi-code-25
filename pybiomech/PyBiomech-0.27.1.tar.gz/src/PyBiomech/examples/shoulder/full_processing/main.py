# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 10:39:01 2017

@author: u0078867
"""


import sys
import os

modPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../../')
sys.path.append(modPath)


from PyBiomech import procedure_sr as proc
from PyBiomech import fio




# Set arguments
filePathC3D = './Passive Abduction03.c3d'

#paramsReadingMethod = 'from_params.json'
paramsReadingMethod = 'from_mimics'
filePathSRParams = './params.json'
filePathMarkersLoc = './landmarks.mimics.txt'

filePathSTLScapula = './scapula.stl'
filePathSTLHumerus = './humerus.stl'

folderPosesSceneFiles = './poses_scenes'





if paramsReadingMethod == 'from_params.json':

    # Read params JSON file and adjust a few structures for later
    params = fio.readORParamsFile(filePathSRParams)
    markersLoc = {m: params['mkrsLoc'][m]['pos'] for m in params['mkrsLoc']}
    side = params['side']

elif paramsReadingMethod == 'from_mimics':
    
    # Read Mimics files and adjust a few structures for later
    params = fio.readMimics(filePathMarkersLoc, ['markers'])
    markersLoc = {m: params['markers'][m] for m in params['markers']}
    side = 'L'

# Read C3D file
print('==== Reading C3D file ...')
markers = fio.readC3D(filePathC3D, ['markers'], {
    'setMarkersZeroValuesToNaN': True,
    'removeSegmentNameFromMarkerNames': True,
})['markers']

# Calculate knee segments poses
vtkScapula = fio.readSTL(filePathSTLScapula)
vtkHumerus = fio.readSTL(filePathSTLHumerus)
poses = proc.calculateShoulderSegmentsPoses(
                                        markers,
                                        markersLoc,
                                        verbose = True,
                                        saveScene = False,
                                        #sceneFrames = range(0, 1700),
                                        vtkScapula = vtkScapula,
                                        vtkHumerus = vtkHumerus,
                                        sceneFormats = ['vtm'],
                                        outputDirSceneFile = folderPosesSceneFiles,
                                       )
                                      
# Calculate knee kinematics data
RT1 = poses['scapula_pose']
RT2 = poses['humerus_pose']
kine = proc.calculateShoulderKinematics(
                                    RT1,
                                    RT2,
                                    markersLoc,
                                    side
                                   )
                                   

                                        
# Assemble all shoulder data
shoulderData = proc.assembleShoulderDataAsIsNoMetadata(
                                                markers=markers, 
                                                poses=poses, 
                                                kine=kine, 
                                              )

                                        
# Save data for file
print('==== Saving shoulder data ...')
fio.writeMATFile('Passive Abduction03.mat', shoulderData)


print('==== Finished!')








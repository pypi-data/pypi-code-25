"""
.. module:: procedure_or
   :synopsis: helper module for procedures used with Oxford-Rig (IORT UZLeuven)

"""

import numpy as np

import fio, kine, spine

import os
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

   
    
    
    

def performSpineAnalysis(
                        markers1,
                        markers2,
                        singleMarkersDescFile,
                        segmentsDescFile,
                        clustersDescDir,
                        spinePointNames,
                        resultsDir,
                        frames = None,
                        sagSpineSplineOrder=3,
                        froSpineSplineOrder=3,
                        savePlots=True,
                        ):
                            
    # calculate THORAX anatomical reference frame for acquisition system 1
    markers1Tho = {}
    markers1Tho['IJ'] = markers1['CLAV']
    markers1Tho['PX'] = markers1['STRN']
    markers1Tho['C7'] = markers1['C7']
    markers1Tho['T8'] = markers1['T9']
    RTho1, OTho1 = kine.thoraxPoseISB(markers1Tho)
    RTTho1 = kine.composeRotoTranslMatrix(RTho1, OTho1)
    RTTho1i = kine.inv2(RTTho1)
    
    # calculate PELVIS anatomical reference frame for acquisition system 1
    RPel1, OPel1 = kine.pelvisPoseISB(markers1, s='R')
    RTPel1 = kine.composeRotoTranslMatrix(RPel1, OPel1)
    RTPel1i = kine.inv2(RTPel1)
    
    # calculate THORAX anatomical reference frame for acquisition system 2
    markers2Tho = {}
    markers2Tho['IJ'] = markers2['CLAV']
    markers2Tho['PX'] = markers2['STRN']
    markers2Tho['C7'] = markers2['C7']
    markers2Tho['T8'] = markers2['T9']
    RTho2, OTho2 = kine.thoraxPoseISB(markers2Tho)
    RTTho2 = kine.composeRotoTranslMatrix(RTho2, OTho2)
    
    # calculate PELVIS anatomical reference frame for acquisition system 2
    RPel2, OPel2 = kine.pelvisPoseISB(markers2, s='R')
    RTPel2 = kine.composeRotoTranslMatrix(RPel2, OPel2)
    RTPel2i = kine.inv2(RTPel2)
    
    # Handles single markers
    markers2New = {}
    singleMarkersInfo = fio.readStringListMapFile(singleMarkersDescFile)
    for m in singleMarkersInfo:
        markerName = m
        segment = singleMarkersInfo[m][0]
        
        # Express real marker in anatomical reference frame 
        if segment == 'thorax':
            RT1i = RTTho1i
        elif segment == 'pelvis':
            RT1i = RTPel1i
        else:
            raise Exception('segment must be one of: thorax, pelvis')
        targetMarkers = {}
        targetMarkers[markerName + ' base'] = markers1[markerName + ' base']
        targetMarkers['True ' + markerName] = markers1['True ' + markerName]
        targetMarkersLoc = kine.changeMarkersReferenceFrame(targetMarkers, RT1i)
        
        #
        if segment == 'thorax':
            RT2 = RTTho2
        elif segment == 'pelvis':
            RT2 = RTPel2
        else:
            raise Exception('segment must be one of: thorax, pelvis')
        markers2New.update(kine.changeMarkersReferenceFrame(targetMarkersLoc, RT2))
        
    
    # Handles clusters
    segmentsInfo = fio.readStringListMapFile(segmentsDescFile)
    print segmentsInfo
    
    for s in segmentsInfo:
        segmentName = s
        clusterType = segmentsInfo[s][0]
        print('%s %s' % (segmentName, clusterType))
        
        # Read data for cluster connected to current segment
        clusterInfo = fio.readStringListMapFile(os.path.join(clustersDescDir, clusterType + '.txt'))
        clusterInfo = {m: np.array(clusterInfo[m]) for m in clusterInfo}
        
        # Modify cluster marker names with real ones
        clusterInfoSpec = clusterInfo.copy()
        subs = segmentsInfo[s][1:]
        clusterBaseName = clusterBaseNameSpec = 'Base'
        for sub in subs:
            s = sub.split(':')
            if s[0] == clusterBaseName:
                clusterBaseNameSpec = s[1]
            del clusterInfoSpec[s[0]]
            clusterInfoSpec[s[1]] = clusterInfo[s[0]]
        print(clusterInfoSpec)
        
        # SVD for acquisition system 1
        args = {}
        markersLoc = clusterInfoSpec.copy()
        args['mkrsLoc'] = markersLoc
        args['verbose'] = True
        args['useOriginFromTrilat'] = False
        mkrList = markersLoc.keys()
        R1, T1, infoSVD1 = kine.rigidBodySVDFun2(markers1, mkrList, args)
        RT1 = kine.composeRotoTranslMatrix(R1, T1)
        
        # Express cluster base and real marker in cluster reference frame
        RT1i = kine.inv2(RT1)
        targetMarkers = {}
        targetMarkers[clusterBaseNameSpec + ' 1'] = markers1[clusterBaseNameSpec]
        targetMarkers['True ' + segmentName] = markers1['True ' + segmentName]
        targetMarkersLoc = kine.changeMarkersReferenceFrame(targetMarkers, RT1i)
        
        # SVD for acquisition system 2
        clusterBaseMarkerLoc = clusterInfoSpec[clusterBaseNameSpec]
        args = {}
        markersLoc = clusterInfoSpec.copy()
        del markersLoc[clusterBaseNameSpec]
        args['mkrsLoc'] = markersLoc
        args['verbose'] = True
        args['useOriginFromTrilat'] = False
        mkrList = markersLoc.keys()
        R2, T2, infoSVD2 = kine.rigidBodySVDFun2(markers2, mkrList, args)
        RT2 = kine.composeRotoTranslMatrix(R2, T2)
        
        # Copy and rename cluster base marker to be expressed in system 2 in global reference frame
        targetMarkersLoc[clusterBaseNameSpec + ' 2'] = clusterBaseMarkerLoc
        
        # Update list of markers for system 2 in global reference frame
        markers2New.update(kine.changeMarkersReferenceFrame(targetMarkersLoc, RT2))
    
    # Express spine points in pelvis reference frame
    spinePoints = {m: markers2New[m] for m in spinePointNames}
    spinePointsPel = kine.changeMarkersReferenceFrame(spinePoints, RTPel2i)
    
    # Merge spine points in one array
    spineData = np.stack([spinePointsPel[m] for m in spinePointNames], axis=2)  # Nf x 3 x Np
    
    # Init results
    res = {}
    res['newMarkers'] = markers2New
    sup, inf = spinePointNames[:-1], spinePointNames[1:]
    spineAngleNames = [sup[i] + '_' + inf[i] for i in xrange(len(sup))]
    Nf = spineData.shape[0]
    res['spineAngles'] = {}
    res['spineAngles']['sagittal'] = {a: np.zeros((Nf,)) for a in spineAngleNames}
    res['spineAngles']['frontal'] = {a: np.zeros((Nf,)) for a in spineAngleNames}
    
    # Create results directory if not existing
    if not os.path.exists(resultsDir):
        os.mkdir(resultsDir)
        
    iRange = range(Nf)
    if frames is not None:
        iRange = frames
    
    # Process data
    for i in iRange:
        
        print('processing time frame %d ...' % i)        
        
        # Interpolate spline in sagittal plane
        spineDataSag = spineData[i,0:2,:].T # Np x 2
        Np = spineDataSag.shape[0]
        spineLineSag = spine.create2DSpline(spineDataSag, order=sagSpineSplineOrder)
        
        # Calculate slope of spine normal at the wanted points
        spineLineSagDer = spine.calcSplineTangentSlopes(spineDataSag, u='only_pts')
        normalSlopesSag = -spineLineSagDer[:,0] / spineLineSagDer[:,1]

        # Calculate angles between segments
        m1, m2 = normalSlopesSag[:-1], normalSlopesSag[1:]
        angles = spine.calcInterlinesAngle(m1, m2)
        for j in xrange(len(spineAngleNames)):
            res['spineAngles']['sagittal'][spineAngleNames[j]][i] = angles[j]
            
        # Interpolate spline in frontal plane
        spineDataFro = spineData[i,2:0:-1,:].T # Np x 2
        Np = spineDataFro.shape[0]
        spineLineFro = spine.create2DSpline(spineDataFro, order=froSpineSplineOrder)
        
        # Calculate slope of spine normal at the wanted points
        spineLineFroDer = spine.calcSplineTangentSlopes(spineDataFro, u='only_pts')
        normalSlopesFro = -spineLineFroDer[:,0] / spineLineFroDer[:,1]

        # Calculate angles between segments
        m1, m2 = normalSlopesFro[:-1], normalSlopesFro[1:]
        angles = spine.calcInterlinesAngle(m1, m2)
        for j in xrange(len(spineAngleNames)):
            res['spineAngles']['frontal'][spineAngleNames[j]][i] = angles[j]
        
        if savePlots:
            
            # Create results directory if not existing
            figuresDir = os.path.join(resultsDir, 'figures')
            if not os.path.exists(figuresDir):
                os.mkdir(figuresDir)
            
            # Plot spine in 3D
#            fig = plt.figure()
#            ax = fig.gca(projection='3d')
#            ax.scatter(spineData[i,2,:], spineData[i,0,:], spineData[i,1,:])
#            mplh.set_axes_equal(ax)
#            plt.show()
            
            # Plot spine in sagittal/frontal plane
            fig = plt.figure()
            
            plt.subplot(1, 2, 1)
            plt.plot(spineDataSag[:,0], spineDataSag[:,1], 'o')
            plt.plot(spineLineSag[:,0], spineLineSag[:,1], lw=3)
            ax = plt.gca()
            xlim, ylim = ax.get_xlim(), ax.get_ylim()
            xN = np.tile([-1000, 1000], [Np, 1])
            yN = (xN - spineDataSag[:,:1]) * normalSlopesSag[:,None] + spineDataSag[:,1:2]
            plt.plot(xN.T, yN.T, 'k')
            plt.axis('equal')
            ax.set_xlim(xlim)
            ax.set_ylim(ylim)
            plt.title('Sagittal')
            plt.xlabel('X pelvis (anterior +)')
            plt.ylabel('Y pelvis (up +)')
            
            plt.subplot(1, 2, 2)
#            plt.plot(spineData[i,2,:], spineData[i,1,:], 'o')
#            plt.axis('equal')
#            plt.title('Frontal')
#            plt.xlabel('Z pelvis (right +)')
            plt.plot(spineDataFro[:,0], spineDataFro[:,1], 'o')
            plt.plot(spineLineFro[:,0], spineLineFro[:,1], lw=3)
            ax = plt.gca()
            xlim, ylim = ax.get_xlim(), ax.get_ylim()
            xN = np.tile([-1000, 1000], [Np, 1])
            yN = (xN - spineDataFro[:,:1]) * normalSlopesFro[:,None] + spineDataFro[:,1:2]
            plt.plot(xN.T, yN.T, 'k')
            plt.axis('equal')
            ax.set_xlim(xlim)
            ax.set_ylim(ylim)
            plt.title('Frontal')
            plt.xlabel('Z pelvis (right +)')
            
            plt.savefig(os.path.join(figuresDir, 'tf_%04d.png' % i), format='png', orientation='landscape')
    
    # Create MATLAB-friendly reslts structure
    def adjustDictForML(d):
        dML = {}
        for k in d:
            kML = k.replace(' ', '_')
            dML[kML] = d[k]
        return dML
    resML = res.copy()
    resML['newMarkers'] = adjustDictForML(res['newMarkers'])        
    resML['spineAngles']['sagittal'] = adjustDictForML(res['spineAngles']['sagittal'])
    
    # Save data to MAT file
    fio.writeMATFile(os.path.join(resultsDir, 'results.mat'), resML)
        
    return res
    
    
    

    
    
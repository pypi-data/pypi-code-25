import math
from . import sonarDist
from . import sm
from . import util
from . import gridMap
from . import dynamicGridMap
from . import dynamicCountingGridMap
from . import bayesMap
reload(bayesMap)

class MapMaker(sm.SM):
#!    def __init__(self, x_min, x_max, y_min, y_max, gridSquareSize):
    """
    It violates the state machine protocol because it changes the grid
    map by side effect, rather than making a fresh copy each time.
    """
    def __init__(self, x_min, x_max, y_min, y_max, gridSquareSize,
                 useClearInfo = False, useCountingMap = False,
                 useBayesMap = True): 

        if useCountingMap:
            gm = dynamicCountingGridMap.DynamicCountingGridMap(\
                                        x_min, x_max, y_min, y_max, gridSquareSize)
        elif useBayesMap:
            gm = bayesMap.BayesGridMap(x_min, x_max, y_min, y_max, gridSquareSize)
        else:
            gm = dynamicGridMap.DynamicGridMap(x_min, x_max, y_min, y_max,
                                               gridSquareSize)
        self.start_state = gm
        self.useClearInfo = useClearInfo or useBayesMap
        if useClearInfo: print('Using clear info')
#!
#!         self.start_state = None   # change this
#!
    def get_next_values(self, state, inp):
#!        pass        
        """
        :param inp: instance of ``SensorInput``
        :param state: is ``grid``

        Modifies grid
        """
        grid = state
        robotPose = inp.odometry
#         if self.useClearInfo:
#             self.clearUnderRobot(grid, robotPose)
        self.processSonarReadings(grid, robotPose, inp.sonars)
        return (grid, grid)

    def processSonarReadings(self, grid, robotPose, sonars):
        """
        For each reading that is less than the reliable length, set the
        point at the end to be occupied and the points along the ray up
        to that point to be free.
        """
        for (sonarPose, d) in zip(sonarDist.sonarPoses, sonars):
            # location of sensor in global frame
            s = grid.pointToIndices(robotPose.transform_point(\
                sonarPose.point()))
            if d < sonarDist.sonarMax:
                # location of sonar 'hit point' in global frame
                h = grid.pointToIndices(\
                         sonarDist.sonarHit(d, sonarPose, robotPose))
                # clear list of grid points on the line between the sensor
                # and the hit point, not including the hit point
                if self.useClearInfo:
                    for ci in util.line_indices(s, h)[:-1]:
                        grid.clearCell(ci)
                # Fill in the end point of the reading
                grid.setCell(h)
            else:
                # assume clear if no return (risky)
                d = sonarDist.sonarMax
                h = grid.pointToIndices(\
                         sonarDist.sonarHit(d, sonarPose, robotPose))
                # clear list of grid points on the line between the sensor
                # and the hit point, not including the hit point
                if self.useClearInfo:
                    for ci in util.line_indices(s, h)[:-1]:
                        grid.clearCell(ci)
                
    def clearUnderRobot(self, grid, robotPose):
        rr =  (int(gridMap.robotRadius / grid.xStep) - 1) * grid.xStep
        corners = \
          [grid.pointToIndices(robotPose.transform_point(util.Point(rr, rr))),
           grid.pointToIndices(robotPose.transform_point(util.Point(rr, -rr))),
           grid.pointToIndices(robotPose.transform_point(util.Point(-rr, rr))),
           grid.pointToIndices(robotPose.transform_point(util.Point(-rr, -rr)))]
        minX = min([cx for (cx, cy) in corners])
        maxX = max([cx for (cx, cy) in corners])
        minY = min([cy for (cx, cy) in corners])
        maxY = max([cy for (cx, cy) in corners])
        for ix in range(minX, maxX+1):
            for iy in range(minY, maxY+1):
                grid.clearCell((ix, iy))

#!                
                
# For testing your map maker
class SensorInput:
    def __init__(self, sonars, odometry):
        self.sonars = sonars
        self.odometry = odometry

testData = [SensorInput([0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2],
                        util.Pose(1.0, 2.0, 0.0)),
            SensorInput([0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4],
                        util.Pose(4.0, 2.0, -math.pi))]

testClearData = [SensorInput([1.0, 5.0, 5.0, 1.0, 1.0, 5.0, 5.0, 1.0],
                             util.Pose(1.0, 2.0, 0.0)),
                 SensorInput([1.0, 5.0, 5.0, 1.0, 1.0, 5.0, 5.0, 1.0],
                             util.Pose(4.0, 2.0, -math.pi))]

def testMapMaker(data):
    (x_min, x_max, y_min, y_max, gridSquareSize) = (0, 5, 0, 5, 0.1)
    mapper = MapMaker(x_min, x_max, y_min, y_max, gridSquareSize)
    mapper.transduce(data)
    mapper.start_state.drawWorld()

def testMapMakerClear(data):
    (x_min, x_max, y_min, y_max, gridSquareSize) = (0, 5, 0, 5, 0.1)
    mapper = MapMaker(x_min, x_max, y_min, y_max, gridSquareSize)
    for i in range(50):
        for j in range(50):
            mapper.start_state.setCell((i, j))
    mapper.transduce(data)
    mapper.start_state.drawWorld()

def testMapMakerN(n, data):
    (x_min, x_max, y_min, y_max, gridSquareSize) = (0, 5, 0, 5, 0.1)
    mapper = MapMaker(x_min, x_max, y_min, y_max, gridSquareSize)
    mapper.transduce(data*n)
    mapper.start_state.drawWorld()

testClearData = [SensorInput([1.0, 5.0, 5.0, 1.0, 1.0, 5.0, 5.0, 1.0],
                             util.Pose(1.0, 2.0, 0.0)),
                 SensorInput([1.0, 5.0, 5.0, 1.0, 1.0, 5.0, 5.0, 1.0],
                             util.Pose(4.0, 2.0, -math.pi))]


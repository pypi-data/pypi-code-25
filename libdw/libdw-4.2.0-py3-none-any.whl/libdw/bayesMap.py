from . import dist
from . import util
from . import colors
from . import ssm
from . import seFast
from . import dynamicGridMap

falsePos = 0.3
falseNeg = 0.3

initPOcc = 0.1
occThreshold = 0.8

#!
# Define the stochastic state-machine model for a given cell here.

# Observation model:  P(obs | state)
def oGivenS(s):
#!    pass    
    if s == 'empty':
        return dist.DDist({'hit': falsePos, 'free': 1 - falsePos})
    else: # occ
        return dist.DDist({'hit': 1 - falseNeg, 'free': falseNeg})
#!
# Transition model: P(new_state | s | a)
def uGivenAS(a):
#!     pass    
    return lambda s: dist.DDist({s: 1.0})
#!
#!cellSSM = None   # Your code here
cellSSM = ssm.StochasticSM(dist.DDist({'occ': initPOcc, 'empty': 1 - initPOcc}),
                           uGivenAS, oGivenS)

#!

class BayesGridMap(dynamicGridMap.DynamicGridMap):

    def squareColor(self, coordinateIndices):
        (xIndex, yIndex) = coordinateIndices
        p = self.occProb((xIndex, yIndex))
        if self.robotCanOccupy((xIndex,yIndex)):
            return colors.probToMapColor(p, colors.greenHue)
        elif self.occupied((xIndex, yIndex)):
            return 'black'
        else:
            return 'red'
        
    def occProb(self, coordinateIndices):
#!        pass        
        (xIndex, yIndex) = coordinateIndices
        return self.grid[xIndex][yIndex].state.prob('occ')
#!
    def makeStartingGrid(self):
#!        pass        
        def makeEstimator(ix, iy):
            m = seFast.StateEstimator(cellSSM)
            m.start()
            return m
        return util.make_2d_array_fill(self.xN, self.yN, makeEstimator)
#!
    def setCell(self, coordinateIndices):
#!        pass        
        
        (xIndex, yIndex) = coordinateIndices
        self.grid[xIndex][yIndex].step(('hit', None))
        self.drawSquare((xIndex, yIndex))
#!        
    def clearCell(self, coordinateIndices):
#!        pass        
        (xIndex, yIndex) = coordinateIndices
        self.grid[xIndex][yIndex].step(('free', None))
        self.drawSquare((xIndex, yIndex))
#!
    def occupied(self, coordinateIndices):
#!        pass        
        (xIndex, yIndex) = coordinateIndices
        return self.occProb((xIndex, yIndex)) > occThreshold

    def explored(self, coordinateIndices):
        (xIndex, yIndex) = coordinateIndices
        p = self.grid[xIndex][yIndex].state.prob('occ')
        return p > 0.8 or p < 0.1

    def cost(self, coordinateIndices):
        (xIndex, yIndex) = coordinateIndices
        cost = 0
        for dx in range(0, self.growRadiusInCells + 1):
            for dy in range(0, self.growRadiusInCells + 1):
                xPlus = util.clip(xIndex+dx, 0, self.xN-1)
                x_minus = util.clip(xIndex-dx, 0, self.xN-1)
                yPlus = util.clip(yIndex+dy, 0, self.yN-1)
                y_minus = util.clip(yIndex-dy, 0, self.yN-1)
                cost = max(cost, self.cost1((xPlus, yPlus)),
                           self.cost1((xPlus,y_minus)),
                           self.cost1((x_minus, yPlus)),
                           self.cost1((x_minus, y_minus)))
        return cost

    def cost1(self, coordinateIndices):
        (xIndex, yIndex) = coordinateIndices
        return self.grid[xIndex][yIndex].state.prob('occ')
#!

mostlyHits = [('hit', None), ('hit', None), ('hit', None), ('free', None)]
mostlyFree = [('free', None), ('free', None), ('free', None), ('hit', None)]

def testCellDynamics(cellSSM, input):
    se = seFast.StateEstimator(cellSSM)
    return se.transduce(input)


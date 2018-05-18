from . import gridMap
import math
from . import util
from . import colors

class DynamicCountingGridMap(gridMap.GridMap):
    """
    Implements the ``GridMap`` interface.
    """
    def __init__(self, x_min, x_max, y_min, y_max, gridSquareSize):
        """
        :param fixMe
        """
        self.x_min = x_min
        """X coordinate of left edge"""
        self.x_max = x_max
        """X coordinate of right edge"""
        self.y_min = y_min
        """Y coordinate of bottom edge"""
        self.y_max = y_max
        """Y coordinate of top edge"""
        self.xN = int(math.ceil(self.x_max / gridSquareSize))
        """number of cells in x dimension"""
        self.yN = int(math.ceil(self.y_max / gridSquareSize))
        """number of cells in y dimension"""
        self.xStep = gridSquareSize
        """size of a side of a cell in the x dimension"""
        self.yStep = gridSquareSize
        """size of a side of a cell in the y dimension"""

        ## Readjust the max dimensions to handle the fact that we need
        ## to have a discrete numer of grid cells
        self.x_max = gridSquareSize * self.xN
        self.y_max = gridSquareSize * self.yN

        self.grid = util.make_2d_array(self.xN, self.yN, 0)
        """values stored in the grid cells"""

        self.growRadiusInCells = int(math.ceil(gridMap.robotRadius\
                                               / gridSquareSize))
        self.makeWindow()
        self.drawWorld()

    def squareColor(self, indices):
        """
        :param documentme
        """
        (xIndex, yIndex) = indices
        maxValue = 10
        storedValue = util.clip(self.grid[xIndex][yIndex], -maxValue, maxValue)
        v = util.clip((maxValue - storedValue) / maxValue, 0, 1)
        s = util.clip((storedValue + maxValue) / maxValue, 0, 1)
        if self.robotCanOccupy(indices):
            hue = colors.greenHue
        else:
            hue = colors.redHue
        return colors.RGBToPyColor(colors.HSVtoRGB(hue, 0.2 + 0.8 * s, v))

    def setCell(self, coordinateIndices):
        (xIndex, yIndex) = coordinateIndices
        self.grid[xIndex][yIndex] += 2
        self.drawSquare((xIndex, yIndex))
        
    def clearCell(self, coordinateIndices):
        (xIndex, yIndex) = coordinateIndices
        self.grid[xIndex][yIndex] -= 0.25
        self.drawSquare((xIndex, yIndex))

    def occupied(self, coordinateIndices):
        (xIndex, yIndex) = coordinateIndices
        return self.grid[xIndex][yIndex] > 2

    def robotCanOccupy(self, coordinateIndices):
        # Really inefficient.  Should cache this in another array and
        # update it when we update grid cells.
        (xIndex, yIndex) = coordinateIndices
        for dx in range(0, self.growRadiusInCells + 1):
            for dy in range(0, self.growRadiusInCells + 1):
                xPlus = util.clip(xIndex+dx, 0, self.xN-1)
                x_minus = util.clip(xIndex-dx, 0, self.xN-1)
                yPlus = util.clip(yIndex+dy, 0, self.yN-1)
                y_minus = util.clip(yIndex-dy, 0, self.yN-1)
                if self.grid[xPlus][yPlus] > 2 or \
                   self.grid[xPlus][y_minus] > 2 or \
                   self.grid[x_minus][yPlus] > 2 or \
                   self.grid[x_minus][y_minus] > 2:
                    return False
        return True

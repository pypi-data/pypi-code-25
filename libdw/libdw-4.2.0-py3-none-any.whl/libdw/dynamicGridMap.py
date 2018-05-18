"""
Grid map class that allows values to be set and cleared dynamically.
"""

import math
from . import util
from . import gridMap
reload(gridMap)

class DynamicGridMap(gridMap.GridMap):
    """
    Implements the ``GridMap`` interface.
    """
    def __init__(self, x_min, x_max, y_min, y_max, gridSquareSize):
        self.growRadiusInCells = int(math.ceil(gridMap.robotRadius \
                                                           / gridSquareSize))
        gridMap.GridMap.__init__(self, x_min, x_max, y_min, y_max, gridSquareSize)

    def makeStartingGrid(self):
        """
        Returns the initial value for ``self.grid``.  Can depend on
        ``self.xN`` and ``self.yN`` being set.

        In this case, the grid is an array filled with the value
        ``False``, meaning that the cells are not occupied.
        """
        return util.make_2d_array(self.xN, self.yN, False)

    def squareColor(self, indices):
        """
        :param indices: ``(ix, iy)`` indices of a grid cell
        :returns: a color string indicating what color that cell
         should be drawn in.
        """
        if self.occupied(indices):
            return 'black'
        elif self.robotCanOccupy(indices):
            return 'white'
        else:  # free in input space, but not in cspace
            return 'gray'

    def setCell(self, coordinateIndices):
        """
        Takes indices for a grid cell, and updates it, given
        information that it contains an obstacle.  In this case, it
        sets the cell to ``True``, and redraws it if its color has changed.
        """
        (xIndex, yIndex) = coordinateIndices
        changed = self.grid[xIndex][yIndex] == False
        self.grid[xIndex][yIndex] = True
        if changed:
            self.drawSquare((xIndex, yIndex))
        
    def clearCell(self, coordinateIndices):
        """
        Takes indices for a grid cell, and updates it, given
        information that it does not contain an obstacle.  In this case, it
        sets the cell to ``True``, and redraws it if its color has changed.
        """
        (xIndex, yIndex) = coordinateIndices
        changed = self.grid[xIndex][yIndex] == True
        self.grid[xIndex][yIndex] = False
        if changed:
            self.drawSquare((xIndex, yIndex))

    def robotCanOccupy(self, coordinateIndices):
        """
        Returns ``True`` if the robot's center can be at any location
        within the cell specified by ``(xIndex, yIndex)`` and not cause
        a collision.  This implementation is very slow:  it considers
        a range of boxes around the spcified box, and ensures that
        none of them is ``self.occupied``.
        """
        (xIndex, yIndex) = coordinateIndices
        for dx in range(0, self.growRadiusInCells + 1):
            for dy in range(0, self.growRadiusInCells + 1):
                xPlus = util.clip(xIndex+dx, 0, self.xN-1)
                x_minus = util.clip(xIndex-dx, 0, self.xN-1)
                yPlus = util.clip(yIndex+dy, 0, self.yN-1)
                y_minus = util.clip(yIndex-dy, 0, self.yN-1)
                if self.occupied((xPlus, yPlus)) or \
                       self.occupied((xPlus,y_minus)) or \
                       self.occupied((x_minus, yPlus)) or \
                       self.occupied((x_minus, y_minus)):
                    return False
        return True

    def occupied(self, coordinateIndices):
        """
        Returns ``True`` if there is an obstacle in any part of this
        cell.  Note that it can be the case that a cell is not
        occupied, but the robot cannot occupy it (because if the
        robot's center were in that cell, some part of the robot would
        be in collision.
        """
        (xIndex, yIndex) = coordinateIndices
        return xIndex < 0 or yIndex < 0 or \
                 xIndex >= self.xN or yIndex >= self.yN or \
                 self.grid[xIndex][yIndex]


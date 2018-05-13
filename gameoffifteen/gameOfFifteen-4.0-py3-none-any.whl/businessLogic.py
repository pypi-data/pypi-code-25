from direction import Direction

class BusinessLogic:
    """Business object for sort buttons."""

    RowCount = 4
    ColumnCount = 4
    StandardSolution =  [[  1,  5,  9, 13],
                         [  2,  6, 10, 14],
                         [  3,  7, 11, 15],
                         [  4,  8, 12,  0]]
    VerticalSolution =  [[  1,  2,  3,  4],
                         [  5,  6,  7,  8],
                         [  9, 10, 11, 12],
                         [ 13, 14, 15,  0]]
    SpiralSolution   =  [[  1, 12, 11, 10],
                         [  2, 13,  0,  9],
                         [  3, 14, 15,  8],
                         [  4,  5,  6,  7]]
    ZickZackSolution =  [[  4,  5, 12, 13],
                         [  3,  6, 11, 14],
                         [  2,  7, 10, 15],
                         [  1,  8,  9,  0]]
    HorsePathSolution = [[ 15,  4,  9,  0],
                         [ 10,  7, 12,  1],
                         [  3, 14,  5,  8],
                         [  6, 11,  2, 13]]

    def __init__(self):
        self.Matrix = [[0 for x in range(BusinessLogic.ColumnCount)] for y in range(BusinessLogic.RowCount)] 
        index = 0
        for row in range(0, BusinessLogic.RowCount):
            for column in range(0, BusinessLogic.ColumnCount):
                index = index + 1
                if index < BusinessLogic.RowCount * BusinessLogic.ColumnCount:
                    self.Matrix[column][row] = index
                else:
                    self.Matrix[column][row] = 0
                
    def valueAt(self, column, row):
        """Returns a value in the matrix."""
        return self.Matrix[column][row]
    
    def __rowIndexOfHole(self):
        """Returns the row of the hole."""
        for row in range(0, BusinessLogic.RowCount):
            for column in range(0, BusinessLogic.ColumnCount):
                if self.valueAt(column, row) == 0:
                    return row            
        
    def __columnIndexOfHole(self):
        """Returns the column of the hole."""
        for row in range(0, BusinessLogic.RowCount):
            for column in range(0, BusinessLogic.ColumnCount):
                if self.valueAt(column, row) == 0:
                    return column            
    
    def print(self):
        """Print the current matrix for debugging."""
        for row in range(0, BusinessLogic.RowCount):
            for column in range(0, BusinessLogic.ColumnCount):
                print(repr(self.valueAt(column, row)).rjust(2), end=' ')            
            print ("\n")
        print ("\n")
            
    def shuffle(self):
        """Shuffles a given matrix."""
        for shuffleIndex in range(0, 10000): 
            direction = Direction.getRandomDirection()
            direction = self.__verifyOrChange(direction)
            self.__moveHole(direction)

    def rowOfValue(self, number):
        """Return the row of a specified value."""
        for row in range(0, BusinessLogic.RowCount):
            for column in range(0, BusinessLogic.ColumnCount):
                if self.valueAt(column, row) == number:
                    return row            

    def columnOfValue(self, number):
        """Return the column of a specified value."""
        for row in range(0, BusinessLogic.RowCount):
            for column in range(0, BusinessLogic.ColumnCount):
                if self.valueAt(column, row) == number:
                    return column
                
    def isMovePossible(self, number):
        """Returns True if a move is possible."""
        selectedRow = self.rowOfValue(number)
        selectedColumn = self.columnOfValue(number)
        holeRow = self.rowOfValue(0)
        holeColumn = self.columnOfValue(0)
        if abs(selectedRow - holeRow) >= 1 and selectedColumn == holeColumn:
            return True
        if abs(selectedColumn - holeColumn) >= 1 and selectedRow == holeRow:
            return True
        return False
        
    def MoveToHole(self, column, row):
        """Moves the column/row to the hole."""
        holeRow = self.rowOfValue(0)
        holeColumn = self.columnOfValue(0)
        self.Matrix[holeColumn][holeRow] = self.Matrix[column][row]
        self.Matrix[column][row] = 0
                
    def __verifyOrChange(self, direction):
        """Checks of the direction in the position is possible. If not reverses the direction."""
        columnHole = self.__columnIndexOfHole()
        if columnHole == 0 and direction == Direction.Left:
            return Direction.Right
        if columnHole == BusinessLogic.ColumnCount - 1 and direction == Direction.Right:
            return Direction.Left
        rowHole = self.__rowIndexOfHole()
        if rowHole == 0 and direction == Direction.Up:
            return Direction.Down
        if rowHole == BusinessLogic.RowCount - 1 and direction == Direction.Down:
            return Direction.Up
        return direction
        
    def __moveHole(self, direction):
        """Move the hole in this direction."""
        columnHole = self.__columnIndexOfHole()
        rowHole = self.__rowIndexOfHole()
        # print("colHole={} rowHole={} direction={}".format(columnHole, rowHole, direction))
        if direction == Direction.Left:
            self.Matrix[columnHole][rowHole] = self.Matrix[columnHole - 1][rowHole]
            self.Matrix[columnHole - 1][rowHole] = 0
        if direction == Direction.Right:
            self.Matrix[columnHole][rowHole] = self.Matrix[columnHole + 1][rowHole]
            self.Matrix[columnHole + 1][rowHole] = 0
        if direction == Direction.Up:
            self.Matrix[columnHole][rowHole]  = self.Matrix[columnHole][rowHole - 1]
            self.Matrix[columnHole][rowHole - 1] = 0
        if direction == Direction.Down:
            self.Matrix[columnHole][rowHole]  = self.Matrix[columnHole][rowHole + 1]
            self.Matrix[columnHole][rowHole + 1] = 0

    def allSorted(self):
        """Checks if the matrix is correct sorted."""
        if self.Matrix == BusinessLogic.StandardSolution:
            return "Standard Lösung"
        elif self.Matrix == BusinessLogic.VerticalSolution:
            return "Vertikale Lösung"
        elif self.Matrix == BusinessLogic.SpiralSolution:
            return "Spirale Lösung"
        elif self.Matrix == BusinessLogic.ZickZackSolution:
            return "ZickZack Lösung"
        elif self.Matrix == BusinessLogic.HorsePathSolution:
            return "Springer Pfad Lösung"
        else:
            return None

        
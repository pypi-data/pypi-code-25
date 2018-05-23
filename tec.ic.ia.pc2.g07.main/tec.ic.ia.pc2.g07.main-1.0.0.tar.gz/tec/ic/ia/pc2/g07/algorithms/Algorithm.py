from abc import ABC, abstractmethod
import shutil
import os

"""
This class implement an abstract class as a definition of an algorithm.
"""


class Algorithm(ABC):
    def __init__(self, board):
        self.board = board

    # Function to remove folder with results
    def remove_last_results(self, folder_name):
        if os.path.isdir(folder_name):
            shutil.rmtree(folder_name)
        os.makedirs(folder_name)

    # Abstract function where the algorithm is implemented
    @abstractmethod
    def execute(self):
        pass

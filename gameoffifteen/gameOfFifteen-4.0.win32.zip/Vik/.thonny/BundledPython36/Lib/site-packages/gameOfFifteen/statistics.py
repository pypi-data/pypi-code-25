import os.path
import datetime
import time
from datetime import date
import json


class Statistics:
    
    __relativeRepositoryName__ = r".\Repository\statistic.txt"
    __datetimeformat__ = '%Y-%m-%d %H:%M:%S %Z'
    __gamedurationformat__ = '%H:%M:%S %Z'
    
    def __init__(self):
        if os.path.isfile(Statistics.__relativeRepositoryName__) == False:
            with open(Statistics.__relativeRepositoryName__, mode='w', encoding='utf-8') as file:
                now = datetime.datetime.now()
                data = []
                data.append(str("{} Initialisiere Statistik".format(now.strftime(Statistics.__datetimeformat__))))        
                json.dump(data, file) 

    def add(self, solution, countOfMoves, countOfButtons, gameTimeInSeconds):
        data = self.getStatistics()
        now = datetime.datetime.now().strftime(Statistics.__datetimeformat__)
        with open(Statistics.__relativeRepositoryName__, mode='w', encoding='utf-8') as file:
            entry = str("{} {} Züge={} Knöpfe={} Spieldauer {}".format(now,
                                                                      solution, countOfMoves, countOfButtons,
                                                                      Statistics.formatDuration(gameTimeInSeconds)))        
            data.append(entry)
            json.dump(data, file)
                
    def getStatistics(self):
        with open(Statistics.__relativeRepositoryName__, mode='r', encoding='utf-8') as file:
            data = json.load(file)
            if data is None:
                return []
            return data
            
    def formatDuration(durationInSecs):    
        return str(datetime.timedelta(seconds=int(durationInSecs)))
    
import os
import sys



def getFilePathMap():
    path = os.path.join(os.path.abspath(__file__),'..','..')
    map = {}
    for file in os.listdir(os.path.join(path,'gitignore')):
        if file.endswith('.gitignore'):
            map[file[:file.rindex('.')].lower()] = os.path.join(path,'gitignore',file)
        elif file == 'Global':
            for globalFile in os.listdir(os.path.join(path,'gitignore','Global')):
                if globalFile.endswith('.gitignore'):
                    map[globalFile[:globalFile.rindex('.')]] = os.path.join(path,'gitignore', 'Global', globalFile)
    return map

def getFileContent(path):
    with open(path, 'r') as fr:
        return fr.read()

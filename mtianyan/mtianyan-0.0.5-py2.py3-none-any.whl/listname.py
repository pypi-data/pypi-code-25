import os.path
filepathlist=[]
filenamelist=[]
def processDirectory ( args, dirname, filenames ):
    for filename in filenames:
          file_path=os.path.join(dirname,filename)
          if os.path.isfile(file_path):
            filepathlist.append(file_path)
            filenamelist.append(filename)

def getpatch(path):
    os.path.walk(r'%s'%path, processDirectory, None )
    return filepathlist

getpatch('H:\CodePath\NoteBook\uber_input')
fw = open('data_list.txt','w')
for item in filenamelist:
    fw.write(item+'\n')

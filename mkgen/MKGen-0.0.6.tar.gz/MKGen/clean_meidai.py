import os

from MKGen import settings

path = os.path.join(settings.DATA_DIR, 'meidai.txt')
with open(path, 'rt') as f:
    lines = f.read()

lines = lines.split('\n')

result = ''
for line in lines:
    if line:
        splited = line.split(' ')
        result += splited[1]
        result += '\n'

path = os.path.join(settings.DATA_DIR, 'clean_meidai.txt')
with open(path, 'wt') as f:
    f.write(result)

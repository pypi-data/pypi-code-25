import ftpbackup.json_cleaner as json_cleaner
import json

s = open('.ftpbackup').read()
print(s)

s2 = json_cleaner.remove_comments(s)
print(s2)

j = json.loads(s2)
print(j)

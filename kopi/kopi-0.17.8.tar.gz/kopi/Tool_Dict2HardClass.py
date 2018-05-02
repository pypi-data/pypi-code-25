#!python3
"""
    Hard code the dict to class
    E.g.:
        {
        "A":b
        "B":{
            "bb":1
            "cc":0
            }
        }

    Generates
    class This:
        A = b
        class B:
            bb = 1
            cc = 0
"""
import kopi as kp
SEMICOLON = ":"
EOL = "\n"
TAB = "    "
SPACE = " "
EQUAL = "="
CLASS = "class"
NONE = "None"
D= kp.GetMasterCafe()
f = open("thisclass.py","w")
S = ""
S+= CLASS + SPACE + "Sugar" + SEMICOLON + EOL
for x in D:
    if not isinstance(D[x],dict):
        #S+= x + SPACE + EQUAL + SPACE + str(D[x]) + EOL
        S+= TAB + x + SPACE + EQUAL + SPACE + NONE + EOL

        continue
    S += TAB +CLASS + SPACE + x + SEMICOLON + EOL
    for y in D[x]:
        if not isinstance(D[x][y], dict):
            #S += TAB + y + SPACE + EQUAL + SPACE + str(D[x][y]) + EOL
            S += TAB + TAB + y + SPACE + EQUAL + SPACE + NONE + EOL

            continue
        S += TAB +TAB + CLASS + SPACE + y + SEMICOLON + EOL
        for z in D[x][y]:
            #S += 2*TAB + z + SPACE + EQUAL + SPACE + str(D[x][y][z]) + EOL
            S += TAB + 2*TAB + z + SPACE + EQUAL + SPACE + NONE + EOL

f.write(S)

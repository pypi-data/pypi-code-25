#!python3
"""
    * This module is not used in the main package

    Parse the  cson file (with comment)
    to the Master Dictionary used in brewcson.py

    I need this to restore my previous brewcson.py
    when atom revert the wrong file during a disasterous
    saving process.
"""
SEMICOLON = ":"

LEOL = "\\n"
TAB = "    "
QUOT = "\""
BRA = "{"
KET = "}"
HELP = "\"help\": "
VALUE = "\"value\": "
SHARP ="#"
SPACE = " "
COMMA =","
PLUS ="+"
EOL = "\n"+TAB
SHARP
f=open("Master_Multi.cson")
S=f.read()
f.close()
S=S.split("\n")
R = ""
prevs = ""
R+=TAB
for s in S:
    print([s])
    if len(s) == 0:
        continue
    #1st branch
    if (s[0] != SPACE):

        if prevs[0:8]==TAB*2:
            R += TAB + KET \
                + EOL\
                +KET \
                +COMMA + EOL
        elif prevs[0:4] == TAB:
            R += KET + COMMA+EOL

        if (s[-1] == SEMICOLON) and(s[0]!=SHARP):
            R +=  QUOT + s[:-1]+ QUOT +SEMICOLON\
                + EOL + BRA + EOL
        elif s[0] == SHARP:
            if s[2:9] == "Default":
                R+=  QUOT +EOL + KET + COMMA + EOL
            else:
                helpme = s[2:]
                helpme=helpme.replace("\"","\\\"")
                if prevs[0] != SHARP:
                    R+= TAB + HELP\
                        + QUOT + helpme
                else:
                    R+= LEOL + QUOT + PLUS + "\\" \
                        +EOL + TAB+ TAB\
                        + QUOT + helpme
        else:
            thevalue = s[s.find(SEMICOLON)+1:]
            if thevalue =="true":
                thevalue = "True"
            if thevalue =="false":
                thevalue = "False"
            R   += QUOT\
                + s[:s.find(SEMICOLON)]\
                + QUOT\
                + SEMICOLON\
                + EOL\
                + BRA + EOL\
                + TAB + VALUE\
                + thevalue\
                + COMMA + EOL


    #2nd Brainch
    elif (s[0:4] == TAB) and (s[4] !=SPACE):
        if prevs[0:8] == TAB *2:
            R += TAB + KET +COMMA+ EOL
        if s[4] == SHARP:
            if s[6:13] == "Default":
                R+=  QUOT +EOL + TAB + KET + COMMA + EOL
            else:
                helpme = s[6:]
                helpme=helpme.replace("\"","\\\"")
                if prevs[0:5] != TAB + SHARP:
                    R+=TAB + TAB + HELP\
                        + QUOT + helpme
                else:
                    R+= LEOL + QUOT + PLUS + "\\" \
                        +EOL + TAB+ TAB + TAB + TAB\
                        + QUOT + helpme
        elif s[-1] != SEMICOLON:
            thevalue = s[s.find(SEMICOLON)+1:]
            if thevalue =="true":
                thevalue = "True"
            if thevalue =="false":
                thevalue = "False"
            R   += TAB\
                + QUOT\
                + s[4:s.find(SEMICOLON)]\
                + QUOT\
                + SEMICOLON\
                + EOL\
                + TAB+BRA + EOL\
                + TAB + TAB + VALUE\
                + thevalue\
                + COMMA + EOL
        elif s[-1] == SEMICOLON:
            R += TAB\
                + QUOT\
                + s[4:-1] + QUOT + SEMICOLON + EOL\
                + TAB + BRA + EOL
    elif s[0:8] == TAB*2:
        if s[8] == SHARP:
            if s[10:17] == "Default":
                R+=  QUOT +EOL + TAB*2 + KET+COMMA + EOL
            else:
                helpme = s[10:]
                helpme=helpme.replace("\"","\\\"")
                if prevs[0:9] != TAB + TAB + SHARP:
                    R+=TAB + TAB*2 + HELP\
                        + QUOT + helpme
                else:
                    R+= LEOL + QUOT + PLUS + "\\" \
                        +EOL + TAB*2+ TAB + TAB + TAB\
                        + QUOT + helpme
        elif s[-1] != SEMICOLON:
            thevalue = s[s.find(SEMICOLON)+1:]
            if thevalue =="true":
                thevalue = "True"
            if thevalue =="false":
                thevalue = "False"
            R   += TAB*2\
                + QUOT\
                + s[8:s.find(SEMICOLON)]\
                + QUOT\
                + SEMICOLON\
                + EOL\
                + TAB*2+BRA + EOL\
                + TAB + TAB +TAB+ VALUE\
                + thevalue + COMMA\
                + EOL
    prevs = s



R = "Master=\\\n{\n" + R + "\n}#END"

#print (R)
ff = open("Master_Multi.py","w")
ff.write(R)
ff.close()

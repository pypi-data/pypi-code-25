#! python3
"""
    * This module is not used in the main package

    Parse the Dictionaty iteration in the Main.py
    to Class Object script

    e.g.:
        Cafe["PDF"]["ShowPDF"] --> Cafe.PDF.ShowPDF
"""
#X =Cafe or Latte
import kopi as kp
#D = kp.GetMasterCafe()
#DictName = "Cafe"
D=kp.GetMasterLatte()
DictName = "Latte"


bra = "[\""
ket = "\"]"
dot = "."
bralen = len(bra)
ketlen = len(ket)
f = open("main.py","r")
S = f.read()
f.close()

for x in D:
    if not isinstance(D[x], dict):
        old = DictName + bra + x + ket
        new = DictName + dot + x
        S=S.replace(old, new)
        continue
    for y in D[x]:
        if not isinstance(D[x][y], dict):
            old = DictName + bra + x + ket + bra + y + ket
            new = DictName + dot + x + dot + y
            S=S.replace(old, new)
            continue
        for z in D[x][y]:
            if not isinstance(D[x][y][z], dict):
                old = DictName + bra + x + ket + bra + y + ket + bra + z + ket
                new = DictName + dot + x + dot + y + dot + z
                S=S.replace(old, new)
                continue
            print("Error handling dict")
            print(x,".",y,".",z,":",D[x][y][z])
print("writing...")

f2 = open("New_main.py","w")
f2.write(S)
f2.close()
print("ok")

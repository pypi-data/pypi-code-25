#! python3
"""
    * This module is not used in the main package

    Parse the Dictionaty iteration in the Main.py
    to Class Object script

    e.g.:
        Cafe["PDF"]["ShowPDF"] --> Cafe.PDF.ShowPDF
"""
#X =Cafe or Latte
DictName = "Cafe"
#S="Cafe[\"PDF\"][\"ShowPDF\"]=3\n"+\
#"Cafe[\"a\"]=4xxxxxxxxCafe[\"b\"]=4"


bra = "[\""
ket = "\"]"
bralen = len(bra)
ketlen = len(ket)
f = open("smallmain.py","r")
S = f.read()
f.close()
count = 0
while S.find(DictName + bra) != -1:

    start =[]
    end = []
    name = []
    MainStart = S.find(DictName + bra)
    start += [S.find(bra)]
    end += [S.find(ket)]
    n=0
    name += [S[start[n] + bralen : end[n]]]
    while S[end[n] + ketlen: end[n]+ketlen + bralen] == bra:
        start += [S.find(bra, end[n]+1)]
        end += [S.find(ket, end[n]+1)]
        n += 1
        name += [ S[start[n] + bralen : end[n]]]
    NEW = DictName
    for i in range(len(name)):
        NEW += "."
        NEW += name[i]
    #print("Count", count)
    print("Count", count, ": ", S[MainStart: end[-1]+ ketlen], " --> ", NEW)

    S=S[:MainStart] + NEW + S[end[-1]+ketlen:]
    count += 1
print("writing...")
f2 = open("New_main.py","w")
f2.write(S)
f2.close()
print("ok")

import sys
from subprocess import call
def main():
    if len(sys.argv) != 2:
        print("\tError\treading input\tfile")
        print("Nothing is done")
        return
    MainFileName = sys.argv[1]
    call (["cp", MainFileName, "Bak_"+ MainFileName])
    with open(MainFileName) as f:
        InS = f.readlines()
        OutS = ""
        for s in InS:
            s = s.replace("\\t", "    ")
            s = s.replace('\t', "    ")

            OutS += s

    with open(MainFileName,"w") as f:
        f.write(OutS)

    print ("ok")
    return

if __name__ == "__main__":
    main()

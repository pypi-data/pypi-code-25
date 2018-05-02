#!python3
import random
def char2number(c):
    if c == "g":
        return 1
    elif c == "c":
        return 2
    elif c == "b":
        return 3
    else:
        return 0
def NumberToGu(number):
    if (number == 1):
        return "ぐ"
    elif (number == 2):
        return "ちょき"
    else:
        return "ぱ"
def WhoWin(number1, number2):
    if number1 == 1:
        if number2 == 2:
            return 1
        elif number2 == 3:
            return 2
        else:
            return 0
    if number1 == 2:
        if number2 == 1:
            return 2
        elif number2 == 2:
            return 0
        else:
            return 1
    if number1 ==3:
        if number2 == 1:
            return 1
        elif number2 == 2:
            return 2
        else:
            return 0

Name = input("あなたの名前は ?")
for i in range(len(Name)):
    print(" 　"*i, Name[i])
print("だいすき　！")
print("じゃんけん　しましょう　？")
count = 0
choice = input(str(count) + "] g:ぐ,  c:ちょき, b: ぱ, q:やめる")
while not choice == 'q':
    Result = random.randrange(1,4)
    choice = char2number(choice)
    if choice == 0:
        print("間違えた！もう一回")
    else:
        count += 1
        print ("わたしは:",NumberToGu(Result),
                ",　あなたは:",NumberToGu(choice))
        if WhoWin(Result, choice) ==1:
            print ("わたし の　かち")
        elif WhoWin(Result, choice) ==2:
            print("あなた　の　かち")
        else:
            print("もう一回。")
    print("")
    choice = input(str(count) +"] g:ぐ,  c:ちょき, b: ぱ, q:やめる")

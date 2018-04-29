def printlist(itemlist,level):
    for x in itemlist:
        if isinstance(x, list):
            printlist(x,level+1)
        else:
            for j in range(level):
                print('\t',end='')
            print(x)


'''This loop is used to print out all 
elements, including inner loops'''

x = [1,2,3,[4,5,6,[7,8,9,]]]
printlist(x,0)

def liebiaozs(zhi,yy=0):
    for i in zhi:
        if isinstance(i,list):
            liebiaozs(i,yy+1)
        else:
            for x in range(yy):
                print("\t",end='')
            print(i)


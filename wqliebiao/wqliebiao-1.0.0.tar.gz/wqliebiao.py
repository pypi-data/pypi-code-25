def liebiaozs(zhi):
    for i in zhi:
        if isinstance(i,list):
            liebiaozs(i)
        else:
            print(i)


#!python3
"""
    Misc small function to convert dict to obj
    Can handle nested class object only up to 3 level.
"""
ErrorMessage1 = "I do not support deep nested class !"
def MembersOf(obj):
    # Use dir(obj). But
    # dir(obj) = ['__class__', '__delattr__',... 'member',...]]
    #, so need to filter out those with "__XX__"
    R=[]
    for attr in dir(obj):
        if attr.startswith("__") and attr.endswith("__"):
            continue
        R+=[attr]
    return R


def lsobj(obj):
    for x in MembersOf(obj):
        O_x = getattr(obj, x)
        if not isinstance(O_x, type):
            print("obj.", x, " = ", O_x)
            continue
        for y in MembersOf(O_x):
            O_x_y = getattr( O_x, y )
            if not isinstance(O_x_y, type):
                print("obj.", x,".",y, " = ", O_x_y)
                continue
            for z in MembersOf(O_x_y):
                O_x_y_z = getattr( O_x_y, z )
                if not isinstance(O_x_y_z, type):
                    print("obj.",x,".",y,".",z," = ", O_x_y_z )
                    continue
                print(ErrorMessage1)

def DictToObj(D):
    obj=type("obj",(object,),D)
    for x in D:
        if isinstance(D[x], dict):
            setattr(obj, x, type(x, (object,),D[x]))
            for y in D[x]:
                if isinstance(D[x][y], dict):
                    setattr( getattr(obj, x),
                             y,
                             type(y,(object,), D[x][y])
                             )
                    for z in D[x][y]:
                        if isinstance(D[x][y][z], dict):
                            setattr(getattr(getattr(obj,x),y),
                                z,
                                type(z(object,),D[x][y][z])
                                )
    return obj

def DictToNullObj(D):
    obj=type("obj",(object,),D)
    for x in D:
        if not isinstance(D[x], dict):
            setattr(obj, x, None)
            continue
        setattr(obj, x, type(x, (object,),D[x]))
        for y in D[x]:
            if not isinstance(D[x][y], dict):
                setattr(getattr(obj,x),y, None)
                continue
            setattr( getattr(obj, x),
                     y,
                     type(y,(object,), D[x][y])
                     )
            for z in D[x][y]:
                if not isinstance(D[x][y][z], dict):
                    setattr(getattr(getattr(obj,x),y),z,None)
                    continue
                print(ErrorMessage1)

    return obj

def UpdateObj1WithObj2(substrate, dopant):
    for x in MembersOf(dopant):
        #if dopant.x is not class object
        if getattr(dopant,x) ==None:
            continue
        if not isinstance(getattr(dopant, x),type):
            setattr(substrate, x, getattr(dopant,x))
            continue
        for y in MembersOf(getattr(dopant, x)):
            #if dopant.x.y is not class object
            dopant_x_y = getattr(getattr(dopant, x),y)
            if dopant_x_y ==None:
                continue
            if not isinstance(dopant_x_y,type):
                setattr(getattr(substrate, x), y, dopant_x_y)
                continue
            for z in MembersOf(dopant_x_y):
                #if dopant.x.y.z is not class object
                dopant_x_y_z = getattr(dopant_x_y, z)
                if dopant_x_y_z ==None:
                    continue
                if not isinstance(dopant_x_y_z,type):
                    setattr(getattr(getattr(substrate,x),y),z, dopant_x_y_z)
                    continue
                print(ErrorMessage1)

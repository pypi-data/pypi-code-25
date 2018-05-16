

import re



def _replace_with_class_table( matched ,ctable):
    expr   = matched.group('var')
    symbol = expr[2:-1]
    class_name = symbol.split('.',1)[0]
    name = symbol.split('.',1)[1]
    klass = ctable.get(class_name,{})
    return klass.get(name,expr)

def _replace_with_variant_table( matched ,vtable,extra):
    expr   = matched.group('var')
    symbol = expr[2:-1]
    val = vtable.get(symbol,None)
    if val is None:
        val = extra.get(symbol,expr)

    return val

import copy
_VAR_PATTERN = re.compile(r'\$\{(?P<class>[A-Za-z]\w*\.)?(?P<var>[A-Za-z_]\w*)\}')
def IsConst(expr):
    ret = _VAR_PATTERN.findall(expr)
    return  len(ret) == 0

def GetReferences(expr):
    vlist = _VAR_PATTERN.findall(expr)
    
    if vlist is None:
        return {}
    ctable={}
    for name, val in vlist:
        if name:
            name = name[:-1]
        else:
            name = None
        ctable[name] = val
    return ctable


def String(string, vtable, clone = False):
    

    def _replace(matched):
        klass = matched.group('class')
        var   = matched.group('var')
        if klass:
            klass = klass[:-1]
        obj = vtable.get(klass,{})
        if var in obj:
            return obj[var]
        return matched.group()
    if clone:
        return _VAR_PATTERN.sub(_replace,string)
    else:
        string = _VAR_PATTERN.sub(_replace,string)
        return string

def Dict( scripts, vtable, clone = False):
    d = scripts
    if clone:
        d = copy.deepcopy(scripts)

    for name, val in d.items():
        if isinstance(val,str):
            d[name] = String(val,vtable)
    return d

def List( scripts, vtable, clone = False):
    d = scripts
    if clone:
        d = copy.deepcopy(scripts)
    for i ,val in enumerate(d):
        if isinstance(val,str):
            d[i] = String(val,vtable)
    return d

def _Compile( scripts,vtable,clone = False):
    if scripts is None:
        return None

    ctable={}
    for klass , vdict in vtable.items():
        ctable[klass]={}
        for name, val in vdict.items():
            if isinstance(val,str):
                if _VAR_PATTERN.search( val) is None:
                    ctable[name] = val

    if isinstance(scripts,str):
        return String(scripts,ctable,clone)
    if isinstance(scripts,list):
        return List(scripts,ctable,clone)
    if isinstance(scripts,dict):
        return Dict(scripts,ctable,clone)

    raise Exception('Unsupport type <%s>to intepret'%type(scripts))





    



def Interpret(vtable,ctable = None,extra={}):
    '''
    vtable : vars talbe (to be interpret)
    ctable : class tabe  to replace class.yyy
    '''


    # replace ctable value

    if ctable:
        for name , expr in vtable.items():
            if not isinstance(expr,str):
                continue

            for key in ctable.keys():
                def _creplace( matched ):
                    return _replace_with_class_table(matched ,ctable)

                vtable[name] = re.sub(r'(?P<var>\$\{%s\.\w+\})'%key, _creplace, expr)

    V_PATTERN = re.compile(r'\$\{[A-Za-z_]\w+\}')
    consts  = set()
    variants = {}
    for name,val in extra.items():
        if isinstance(val,str):
            consts.add(name)

    for name , expr in vtable.items():
        if not isinstance(expr,str):
            continue

        var = V_PATTERN.findall(expr)
        
        if var:
            variants[name] = set()
            for v in var:
                variants[name].add(v[2:-1])
        else:
            consts.add(name)

    n = len(variants)

    while n and len(variants):
        n -=1
        for name, var in variants.items():
            expr = vtable[name]
            if not isinstance(expr,str):
                continue

            if var.issubset(consts):
                def _replace(matched):
                    return _replace_with_variant_table(matched,vtable,extra)

                vtable[name] = re.sub(r'(?P<var>\$\{\w+\})', _replace, vtable[name])
                consts.add(name)
                variants.pop(name)
                break



            

         


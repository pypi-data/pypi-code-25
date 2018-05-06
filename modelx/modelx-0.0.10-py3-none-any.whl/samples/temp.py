import modelx as mx


#  root--A--B--foo
#        :
#        C--B'-bar
#    |
#    +---D<-A, B

def foo(x):
    return x

def bar(x):
    return 2 * x

def baz(x):
    return 3 * x

def qux(x):
    return 4 * x

model, root = mx.new_model(), mx.new_space(name='root')
A = root.new_space(name='A')
B = A.new_space('B')
B.new_cells(formula=foo)

C = root.new_space(name='C', bases=A)

C.B.new_cells(formula=baz)





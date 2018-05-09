import numpy as np
from hap import PyHaplotype
from gen import PyGenotype
# from alphahousepython import PyGenotype
# from alphahousepython import PyHaplotype
array = np.ones((10),dtype=np.int8)


array[0] = 4
t = PyHaplotype(array, 0)
t2 = PyHaplotype(array,0)

print ("HEY "+ str(t.start))

print(t.getLength())
print(t.getPhase(0))
print(t.getPhase(1))
t.setPhase(1,0)
print(t.getPhase(1))
print(t.countMissing())
t.setPhase(1, 9)
print(t.countMissing())
print(t.countNotMissing())

print(t.intersectCompare(t2))

print("PRESUB" + str(t))

t = PyHaplotype(np.array([0,1,0,1],dtype=int), 0)
x = t.getSubsetHaplotype(1, 2)

print(x)

t = PyGenotype(np.array([0, 1, 0, 1], dtype=int), 0)
x = t.getSubsetGenotype(1, 2)

print(x)
# print(x.getLength())


# t = PyGenotype(array, 0)

# y = PyGenotype(array, 0)
# print(t)


# print(t.countNotEqualExcludeMissing(y))
# x = t.toIntArray()

# print(x)

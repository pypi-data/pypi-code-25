import nlpk.lib.operator as op
import nlpk.lib.spam as sp


def sum(a, b):
	return op.sum(a, b)

def subtract(a, b):
	return op.substraction(a, b)

def system(cmd):
	return sp.system(cmd)


if __name__ == '__main__':
	a, b = 10, 20

	print(sum(a, b))
	print(subtract(a, b))
	print(system('ls'))

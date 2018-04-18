from ..scanner import Scanner
from sys import argv
from os.path import abspath, isfile

def main():
	if len(argv) >= 3:
		socks = abspath(argv[1])
		output = abspath(argv[2])
		threads = argv[3]

		if not isfile(socks):
			print('{} is not exists.'.format(socks))
			exit()

		try:
			threads = int(threads)
		except ValueError as e:
			print('Threads Must be Integer')
			exit()

		Scanner().checkSocks(socks, threads, output)
	else:
		print(
			"""Usage: pscanner proxyfile outputfile threads

Example:
pscanner proxies.txt validSocks.txt 100"""
)
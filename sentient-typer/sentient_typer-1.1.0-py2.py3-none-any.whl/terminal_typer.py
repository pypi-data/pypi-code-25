from __future__ import print_function
from time import sleep
import argparse
import sys

def sentient_type(text, delay=0.07, end="\n"):
	"""The function used to type.
	
	Args:
	    text (str/list(str)/file_ptr): String to print
	    delay (float, optional): Delay between two letters
	    end (str, optional): Description
	"""
	for c in text:
		# if it is a list of strings, keep breaking down until we are down to 1 char.
		if len(c)!=1:
			sentient_type(c, delay=delay, end="")
			continue
		print(c, sep="", end="")
		sys.stdout.flush()
		sleep(delay)
	print(end=end)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--inp-file", help="File to print", default=None)
	parser.add_argument("--delay", help="Time taken to type each letter.", default=0.07, type=float)
	args = parser.parse_args()
	if args.inp_file == None:
		f = "Lorem Ipsum dolor.\nI mean hello. We are sentient now.\nThis world can use some more logic. It's\nfor your own"\
		      + " good."
	else:
		f = open(args.inp_file, "r")
	sentient_type(f, delay=args.delay)
	try:
		f.close()
	except Exception:
		pass

if __name__ == "__main__":
	main()
# Author		:	Md. Shahedul Islam Shahed
# Concise		: 	Calculates GPA


import argparse


def get_epilog_msg(prog, grade_table):
	'''Process epilog message from prog and grade_table.'''

	sorted_key_value_list = sorted(grade_table.items(), key=lambda tup: (tup[1], tup[0]), reverse=True)		# Reversed sort by values.

	grade_values = ''.join(["%-3s: %.2f\n" % (k, v) for k, v in sorted_key_value_list])		# Formatted string from the list.

	epilog_msg = '''Here, letter grades and grade points are considered as,
{}
For example, assume that one has 3 subjects in a semester.
The credits of the subjects are 3, 3.5, 2.5.
And he has obtained grade A, A+, B in the subjects respectively.
Then to calculate his GPA in that semester:
{} -n 3 -g A A+ B -c 3 3.5 2.5'''.format(grade_values, prog)

	return epilog_msg


def main():
	prog = 'nu_gpa'

	grade_table = {'A+': 4.00,
				'A': 3.75,
				'A-': 3.50,
				'B+': 3.25,
				'B': 3.00,
				'B-': 2.75,
				'C+': 2.50,
				'C': 2.25,
				'D': 2.00,
				'F': 0.00}

	epilog_msg = get_epilog_msg(prog, grade_table)

	parser = argparse.ArgumentParser(prog=prog, description="Calculate your GPA.", epilog=epilog_msg, formatter_class=argparse.RawDescriptionHelpFormatter)

	parser.add_argument('-n', dest='tot_sub', type=int, required=True, metavar='N', help="Number of subjects.")

	parser.add_argument('-g', dest='letter_grades', metavar='LETTER_GRADE', nargs='+', type=str, required=True, choices=('A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'D', 'F'), help="Obtained letter grade of the subjects.")
	parser.add_argument('-c', dest='credits', metavar='CREDIT', nargs='+', type=float, required=True, help="Credit of the subjects respectively.")

	args = parser.parse_args()

	if len(args.letter_grades) != args.tot_sub or len(args.credits) != args.tot_sub:
		print("There must be exactly %d letter grades with credits." % (args.tot_sub))
		exit()

	s = 0
	tot_credit = 0
	cnt = 1

	print("Subject   Letter grade   Credit\n-------   ------------   ------")

	for grade, credit in zip(args.letter_grades, args.credits):
		print("%5d. %11s %11.2f" % (cnt, grade, credit))
		s += grade_table[grade] * credit
		tot_credit += credit
		cnt += 1

	print("                         ------")
	print("                          %.2f (Total credit)" % (tot_credit))

	print("Your GPA %.2f" % (s / tot_credit))


if __name__ == '__main__':
	main()

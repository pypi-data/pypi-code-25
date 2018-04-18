import sys


def pascals_triangle(number_of_rows):

    number_of_rows = int(number_of_rows)
    list_of_lists = []
    for _ in range(number_of_rows):
        row = [1]
        if list_of_lists:
            last_row = list_of_lists[-1]
            row.extend([sum(pair) for pair in zip(last_row, last_row[1:])])
            row.append(1)
        list_of_lists.append(row)
    return list_of_lists


def main():

    for i in pascals_triangle(number_of_rows=sys.argv[1]):
        print(i)


if __name__ == '__main__':

    main()

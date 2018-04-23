import argparse
import sys
import time

parser = argparse.ArgumentParser(description="This runs forever")

if __name__ == '__main__':
    args = parser.parse_args()
    index = 0
    while True:
        index += 1
        sys.stdout.write('Printing message {}\n'.format(index))
        time.sleep(1)

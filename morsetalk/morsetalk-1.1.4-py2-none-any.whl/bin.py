# -*- coding: utf-8 -*-
import argparse
import morsetalk.morse as morse


parser = argparse.ArgumentParser(description='Encode and Decode morse code')
parser.add_argument('--encode', help='String to encode', required=False)
parser.add_argument('--decode', help='String to decode', required=False)

args = parser.parse_args()


def run():
    if args.encode:
        print(morse.encode(args.encode))
    elif args.decode:
        print(morse.decode(args.decode))
    else:
        print('You need to specify either --encode or --decode')

    return
